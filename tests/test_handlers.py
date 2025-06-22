import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram.ext import ConversationHandler

from novel_notify.bot.handlers import BotHandlers, WAITING_FOR_URL
from novel_notify.database.models import NovelMetadata, Chapter, UserSubscription # Changed ChapterMetadata to Chapter

# Test data
TEST_USER_ID = 123
TEST_NOVEL_ID = "12345678901234567" # Webnovel IDs are typically 17 digits
TEST_NOVEL_URL = f"https://www.webnovel.com/book/{TEST_NOVEL_ID}"
INVALID_NOVEL_URL = "https://invalid.url/book/123"

# Sample NovelMetadata
SAMPLE_NOVEL_METADATA = NovelMetadata(
    novel_id=TEST_NOVEL_ID,
    novel_title="Test Novel Title",
    author="Test Author",
    cover_url="http://example.com/cover.jpg", # Changed cover_image_url to cover_url
    latest_chapter=Chapter(
        chapter_number=1, # Added chapter_number
        title="Chapter 1: The Beginning",
        url=f"{TEST_NOVEL_URL}/chapter-1",
        published="2023-01-01 10:00:00"
    ),
    last_updated=1672560000.0  # Example timestamp
)


@pytest.mark.asyncio
async def test_start_command(bot_handlers, mock_update, mock_context):
    """Test the /start command."""
    await bot_handlers.start_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args
    assert "Welcome to Novel Notify Bot!" in call_args[0][0]


@pytest.mark.asyncio
async def test_help_command(bot_handlers, mock_update, mock_context):
    """Test the /help command."""
    await bot_handlers.help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args
    assert "Novel Notify Bot Commands" in call_args[0][0]


@pytest.mark.asyncio
async def test_add_novel_command_with_url(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test /add command when URL is provided as an argument."""
    mock_context.args = [TEST_NOVEL_URL]

    # Mock scraper and database methods
    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockWebNovelScraperClass:
        mock_scraper_instance = MockWebNovelScraperClass.return_value
        mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
        mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)
        mock_scraper_instance.scrape_novel_metadata = AsyncMock(return_value=SAMPLE_NOVEL_METADATA)

        mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])
        mock_db_manager.save_novel_metadata = MagicMock(return_value=True)
        mock_db_manager.add_subscription = MagicMock(return_value=True)

        result = await bot_handlers.add_novel_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        "🔄 **Processing...**\n\nFetching novel information from WebNovel...",
        parse_mode='Markdown'
    )
    # The message should be edited after processing
    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "Novel Added Successfully!" in edit_call_args
    assert result == ConversationHandler.END


@pytest.mark.asyncio
async def test_add_novel_command_no_url(bot_handlers, mock_update, mock_context):
    """Test /add command when no URL is provided, expecting WAITING_FOR_URL state."""
    mock_context.args = []
    result = await bot_handlers.add_novel_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Add a Novel" in call_args
    assert "Please send me the WebNovel URL" in call_args
    assert result == WAITING_FOR_URL


@pytest.mark.asyncio
async def test_receive_url_valid(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test receive_url handler with a valid URL."""
    mock_update.message.text = TEST_NOVEL_URL

    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockWebNovelScraperClass:
        mock_scraper_instance = MockWebNovelScraperClass.return_value
        mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
        mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)
        mock_scraper_instance.scrape_novel_metadata = AsyncMock(return_value=SAMPLE_NOVEL_METADATA)

        mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])
        mock_db_manager.save_novel_metadata = MagicMock(return_value=True)
        mock_db_manager.add_subscription = MagicMock(return_value=True)

        result = await bot_handlers.receive_url(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        "🔄 **Processing...**\n\nFetching novel information from WebNovel...",
        parse_mode='Markdown'
    )
    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "Novel Added Successfully!" in edit_call_args
    assert result == ConversationHandler.END


@pytest.mark.asyncio
async def test_receive_url_invalid(bot_handlers, mock_update, mock_context):
    """Test receive_url handler with an invalid URL."""
    mock_update.message.text = INVALID_NOVEL_URL
    result = await bot_handlers.receive_url(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Invalid URL" in call_args
    assert result == ConversationHandler.END # Still ends conversation


@pytest.mark.asyncio
async def test_cancel_conversation(bot_handlers, mock_update, mock_context):
    """Test the cancel_conversation handler."""
    result = await bot_handlers.cancel_conversation(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with(
        "❌ Operation cancelled.",
        parse_mode='Markdown'
    )
    assert result == ConversationHandler.END


@pytest.mark.asyncio
async def test_list_novels_command_empty(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test /list command when the user has no tracked novels."""
    mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])
    await bot_handlers.list_novels_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "No Novels Tracked" in call_args


@pytest.mark.asyncio
async def test_list_novels_command_with_novels(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test /list command with tracked novels."""
    subscriptions = [UserSubscription(user_id=TEST_USER_ID, novel_id=TEST_NOVEL_ID, notifications_enabled=True)]
    mock_db_manager.get_user_subscriptions = MagicMock(return_value=subscriptions)
    mock_db_manager.get_novel_metadata = MagicMock(return_value=SAMPLE_NOVEL_METADATA)

    await bot_handlers.list_novels_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Your Tracked Novels" in call_args
    assert SAMPLE_NOVEL_METADATA.novel_title in call_args
    assert SAMPLE_NOVEL_METADATA.latest_chapter.title in call_args


@pytest.mark.asyncio
async def test_remove_novel_command_no_args(bot_handlers, mock_update, mock_context):
    """Test /remove command with no arguments."""
    mock_context.args = []
    await bot_handlers.remove_novel_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Remove a Novel" in call_args
    assert "Usage: `/remove <number>`" in call_args


@pytest.mark.asyncio
async def test_remove_novel_command_invalid_number(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test /remove command with an invalid novel number."""
    mock_context.args = ["abc"] # Invalid number
    await bot_handlers.remove_novel_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "Invalid Number" in mock_update.message.reply_text.call_args[0][0]

    mock_context.args = ["0"] # Out of bounds
    mock_db_manager.get_user_subscriptions = MagicMock(return_value=[]) # No subscriptions
    await bot_handlers.remove_novel_command(mock_update, mock_context)
    assert "Please choose a number between 1 and 0" in mock_update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_remove_novel_command_valid(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test /remove command with a valid novel number."""
    mock_context.args = ["1"]
    subscriptions = [UserSubscription(user_id=TEST_USER_ID, novel_id=TEST_NOVEL_ID, notifications_enabled=True)]
    mock_db_manager.get_user_subscriptions = MagicMock(return_value=subscriptions)
    mock_db_manager.get_novel_metadata = MagicMock(return_value=SAMPLE_NOVEL_METADATA)
    mock_db_manager.remove_subscription = MagicMock(return_value=True)

    await bot_handlers.remove_novel_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Novel Removed" in call_args
    assert SAMPLE_NOVEL_METADATA.novel_title in call_args


@pytest.mark.asyncio
async def test_check_updates_command_no_subscriptions(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test /check command when user has no subscriptions."""
    mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])
    await bot_handlers.check_updates_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    assert "No Novels to Check" in mock_update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_check_updates_command_no_updates(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test /check command when there are no new chapter updates."""
    subscriptions = [UserSubscription(user_id=TEST_USER_ID, novel_id=TEST_NOVEL_ID, notifications_enabled=True)]
    mock_db_manager.get_user_subscriptions = MagicMock(return_value=subscriptions)
    mock_db_manager.get_novel_metadata = MagicMock(return_value=SAMPLE_NOVEL_METADATA)

    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockWebNovelScraperClass:
        mock_scraper_instance = MockWebNovelScraperClass.return_value
        mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
        mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)
        # Return the same chapter, indicating no update
        mock_scraper_instance.quick_check_latest_chapter = AsyncMock(return_value=SAMPLE_NOVEL_METADATA.latest_chapter)

        await bot_handlers.check_updates_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        f"🔄 **Checking Updates...**\n\nChecking {len(subscriptions)} novels for updates...",
        parse_mode='Markdown'
    )
    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "No new updates found" in edit_call_args


@pytest.mark.asyncio
async def test_check_updates_command_with_updates(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test /check command when there are new chapter updates."""
    subscriptions = [UserSubscription(user_id=TEST_USER_ID, novel_id=TEST_NOVEL_ID, notifications_enabled=True)]
    mock_db_manager.get_user_subscriptions = MagicMock(return_value=subscriptions)
    mock_db_manager.get_novel_metadata = MagicMock(return_value=SAMPLE_NOVEL_METADATA)

    updated_chapter = Chapter( # Corrected ChapterMetadata to Chapter
        chapter_number=2,
        title="Chapter 2: A New Challenge",
        url=f"{TEST_NOVEL_URL}/chapter-2",
        published="2023-01-02 12:00:00"
    )

    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockWebNovelScraperClass:
        mock_scraper_instance = MockWebNovelScraperClass.return_value
        mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
        mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)
        mock_scraper_instance.quick_check_latest_chapter = AsyncMock(return_value=updated_chapter)

        await bot_handlers.check_updates_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        f"🔄 **Checking Updates...**\n\nChecking {len(subscriptions)} novels for updates...",
        parse_mode='Markdown'
    )
    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "Updates Found!" in edit_call_args
    assert SAMPLE_NOVEL_METADATA.novel_title in edit_call_args
    assert updated_chapter.title in edit_call_args


@pytest.mark.asyncio
async def test_handle_url_message_valid_url(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test handling of a direct message containing a valid WebNovel URL."""
    mock_update.message.text = TEST_NOVEL_URL # Direct message with URL

    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockWebNovelScraperClass:
        mock_scraper_instance = MockWebNovelScraperClass.return_value
        mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
        mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)
        mock_scraper_instance.scrape_novel_metadata = AsyncMock(return_value=SAMPLE_NOVEL_METADATA)

        mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])
        mock_db_manager.save_novel_metadata = MagicMock(return_value=True)
        mock_db_manager.add_subscription = MagicMock(return_value=True)

        await bot_handlers.handle_url_message(mock_update, mock_context)

    # Similar assertions to add_novel_command with URL
    mock_update.message.reply_text.assert_called_once_with(
        "🔄 **Processing...**\n\nFetching novel information from WebNovel...",
        parse_mode='Markdown'
    )
    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "Novel Added Successfully!" in edit_call_args


@pytest.mark.asyncio
async def test_handle_url_message_invalid_text(bot_handlers, mock_update, mock_context):
    """Test handling of a direct message that is not a WebNovel URL."""
    mock_update.message.text = "Hello, this is not a URL."
    await bot_handlers.handle_url_message(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "I don't understand" in call_args

@pytest.mark.asyncio
async def test_process_novel_url_already_subscribed(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test _process_novel_url when the user is already subscribed to the novel."""
    mock_db_manager.get_user_subscriptions = MagicMock(return_value=[
        UserSubscription(user_id=TEST_USER_ID, novel_id=TEST_NOVEL_ID)
    ])

    await bot_handlers._process_novel_url(mock_update, mock_context, TEST_NOVEL_URL)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Already Tracking" in call_args

@pytest.mark.asyncio
async def test_process_novel_url_scraper_fails(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test _process_novel_url when the scraper fails to fetch metadata."""
    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockWebNovelScraperClass:
        mock_scraper_instance = MockWebNovelScraperClass.return_value
        mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
        mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)
        mock_scraper_instance.scrape_novel_metadata = AsyncMock(return_value=None) # Scraper returns None

        mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])

        await bot_handlers._process_novel_url(mock_update, mock_context, TEST_NOVEL_URL)

    mock_update.message.reply_text.assert_called_once_with(
        "🔄 **Processing...**\n\nFetching novel information from WebNovel...",
        parse_mode='Markdown'
    )
    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "Failed to Fetch Novel" in edit_call_args

@pytest.mark.asyncio
async def test_process_novel_url_db_save_metadata_fails(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test _process_novel_url when saving novel metadata to DB fails."""
    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockWebNovelScraperClass:
        mock_scraper_instance = MockWebNovelScraperClass.return_value
        mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
        mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)
        mock_scraper_instance.scrape_novel_metadata = AsyncMock(return_value=SAMPLE_NOVEL_METADATA)

        mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])
        mock_db_manager.save_novel_metadata = MagicMock(return_value=False) # DB save fails

        await bot_handlers._process_novel_url(mock_update, mock_context, TEST_NOVEL_URL)

    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "Database Error" in edit_call_args

@pytest.mark.asyncio
async def test_process_novel_url_db_add_subscription_fails(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test _process_novel_url when adding subscription to DB fails."""
    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockWebNovelScraperClass:
        mock_scraper_instance = MockWebNovelScraperClass.return_value
        mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
        mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)
        mock_scraper_instance.scrape_novel_metadata = AsyncMock(return_value=SAMPLE_NOVEL_METADATA)

        mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])
        mock_db_manager.save_novel_metadata = MagicMock(return_value=True)
        mock_db_manager.add_subscription = MagicMock(return_value=False) # DB add subscription fails

        await bot_handlers._process_novel_url(mock_update, mock_context, TEST_NOVEL_URL)

    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "Subscription Error" in edit_call_args

@pytest.mark.asyncio
async def test_process_novel_url_general_exception(bot_handlers, mock_update, mock_context, mock_db_manager):
    """Test _process_novel_url when a general exception occurs."""
    with patch('novel_notify.bot.handlers.WebNovelScraper', new_callable=AsyncMock) as MockScraper:
        mock_scraper_instance = MockScraper.return_value.__aenter__.return_value
        mock_scraper_instance.scrape_novel_metadata.side_effect = Exception("Unexpected error")

        mock_db_manager.get_user_subscriptions = MagicMock(return_value=[])

        await bot_handlers._process_novel_url(mock_update, mock_context, TEST_NOVEL_URL)

    mock_update.message.reply_text.return_value.edit_text.assert_called_once()
    edit_call_args = mock_update.message.reply_text.return_value.edit_text.call_args[0][0]
    assert "An unexpected error occurred" in edit_call_args
