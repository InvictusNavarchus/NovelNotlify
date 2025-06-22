import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import time

from novel_notify.bot.scheduler import UpdateScheduler
from novel_notify.database import DatabaseManager
from novel_notify.database.models import NovelMetadata, Chapter, UserSubscription
from novel_notify.scraper import WebNovelScraper

# Test data
TEST_NOVEL_ID_SCHED_1 = "sched_novel_1"
TEST_NOVEL_ID_SCHED_2 = "sched_novel_2"
TEST_USER_ID_SCHED_1 = 2001
TEST_USER_ID_SCHED_2 = 2002

CURRENT_CHAPTER_1 = Chapter(chapter_number=10, title="Chapter 10 - Current", url="/ch10", published="Yesterday")
UPDATED_CHAPTER_1 = Chapter(chapter_number=11, title="Chapter 11 - New Update", url="/ch11", published="Today")

METADATA_SCHED_1 = NovelMetadata(
    novel_id=TEST_NOVEL_ID_SCHED_1,
    novel_title="Scheduled Test Novel 1",
    author="Scheduler Author",
    cover_url="http://example.com/sched_cover1.jpg",
    latest_chapter=CURRENT_CHAPTER_1,
    last_updated=time.time()
)

METADATA_SCHED_2 = NovelMetadata(
    novel_id=TEST_NOVEL_ID_SCHED_2,
    novel_title="Scheduled Test Novel 2",
    author="Scheduler Author 2",
    cover_url="http://example.com/sched_cover2.jpg",
    latest_chapter=Chapter(chapter_number=1, title="Fixed Chapter", url="/fch1", published="Two days ago"),
    last_updated=time.time()
)

@pytest.fixture
def mock_db_manager_for_scheduler():
    db_mock = MagicMock(spec=DatabaseManager)
    db_mock.get_all_subscriptions = MagicMock(return_value=[])
    db_mock.get_novel_metadata = MagicMock(return_value=None)
    db_mock.get_novel_subscribers = MagicMock(return_value=[])
    db_mock.save_novel_metadata = MagicMock(return_value=True)
    db_mock.update_last_notified_chapter = MagicMock(return_value=True)
    return db_mock

@pytest.fixture
def mock_bot_for_scheduler():
    bot_mock = AsyncMock()
    bot_mock.send_message = AsyncMock()
    return bot_mock

@pytest.fixture
@patch('novel_notify.bot.scheduler.AsyncIOScheduler')
def update_scheduler(MockAsyncIOScheduler, mock_db_manager_for_scheduler, mock_bot_for_scheduler):
    mock_scheduler_instance = MockAsyncIOScheduler.return_value
    mock_scheduler_instance.add_job = MagicMock()
    mock_scheduler_instance.start = MagicMock()
    mock_scheduler_instance.shutdown = MagicMock()
    scheduler = UpdateScheduler(db_manager=mock_db_manager_for_scheduler, bot=mock_bot_for_scheduler)
    scheduler.scheduler = mock_scheduler_instance
    return scheduler

@pytest.mark.asyncio
async def test_scheduler_initialization(update_scheduler):
    update_scheduler.scheduler.add_job.assert_called_once()

def test_scheduler_start_shutdown(update_scheduler):
    update_scheduler.start()
    update_scheduler.scheduler.start.assert_called_once()
    update_scheduler.shutdown()
    update_scheduler.scheduler.shutdown.assert_called_once_with(wait=False)

@pytest.mark.asyncio
@patch('novel_notify.bot.scheduler.WebNovelScraper')
async def test_check_all_novels_for_updates_no_novels(MockScraperClass, update_scheduler, mock_db_manager_for_scheduler):
    mock_db_manager_for_scheduler.get_all_subscriptions.return_value = []
    mock_instance = AsyncMock(spec=WebNovelScraper)
    MockScraperClass.return_value = mock_instance
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.quick_check_latest_chapter = AsyncMock()
    await update_scheduler.check_all_novels_for_updates()
    mock_instance.quick_check_latest_chapter.assert_not_called()

@pytest.mark.asyncio
@patch('novel_notify.bot.scheduler.WebNovelScraper')
async def test_check_all_novels_for_updates_no_update_found(MockScraperClass, update_scheduler, mock_db_manager_for_scheduler, mock_bot_for_scheduler):
    subs = [UserSubscription(user_id=TEST_USER_ID_SCHED_1, novel_id=TEST_NOVEL_ID_SCHED_1)]
    mock_db_manager_for_scheduler.get_all_subscriptions.return_value = subs
    mock_db_manager_for_scheduler.get_novel_metadata.return_value = METADATA_SCHED_1
    mock_instance = AsyncMock(spec=WebNovelScraper)
    MockScraperClass.return_value = mock_instance
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.quick_check_latest_chapter = AsyncMock(return_value=METADATA_SCHED_1.latest_chapter)
    await update_scheduler.check_all_novels_for_updates()
    mock_instance.quick_check_latest_chapter.assert_called_once_with(TEST_NOVEL_ID_SCHED_1)
    mock_bot_for_scheduler.send_message.assert_not_called()

@pytest.mark.asyncio
@patch('novel_notify.bot.scheduler.WebNovelScraper')
async def test_check_all_novels_for_updates_update_found_and_notify(MockScraperClass, update_scheduler, mock_db_manager_for_scheduler, mock_bot_for_scheduler):
    subs = [UserSubscription(user_id=TEST_USER_ID_SCHED_1, novel_id=TEST_NOVEL_ID_SCHED_1), UserSubscription(user_id=TEST_USER_ID_SCHED_2, novel_id=TEST_NOVEL_ID_SCHED_1)]
    mock_db_manager_for_scheduler.get_all_subscriptions.return_value = subs
    mock_db_manager_for_scheduler.get_novel_metadata.return_value = METADATA_SCHED_1
    mock_db_manager_for_scheduler.get_novel_subscribers.return_value = [TEST_USER_ID_SCHED_1, TEST_USER_ID_SCHED_2]
    mock_instance = AsyncMock(spec=WebNovelScraper)
    MockScraperClass.return_value = mock_instance
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.quick_check_latest_chapter = AsyncMock(return_value=UPDATED_CHAPTER_1)
    await update_scheduler.check_all_novels_for_updates()
    mock_instance.quick_check_latest_chapter.assert_called_once_with(TEST_NOVEL_ID_SCHED_1)
    assert mock_bot_for_scheduler.send_message.call_count == 2

@pytest.mark.asyncio
@patch('novel_notify.bot.scheduler.WebNovelScraper')
async def test_check_single_novel_scraper_fails(MockScraperClass, update_scheduler, mock_db_manager_for_scheduler):
    mock_db_manager_for_scheduler.get_novel_metadata.return_value = METADATA_SCHED_1
    mock_instance = AsyncMock(spec=WebNovelScraper)
    MockScraperClass.return_value = mock_instance
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.quick_check_latest_chapter = AsyncMock(return_value=None)
    mock_db_manager_for_scheduler.get_all_subscriptions.return_value = [UserSubscription(user_id=TEST_USER_ID_SCHED_1, novel_id=TEST_NOVEL_ID_SCHED_1)]
    await update_scheduler.check_all_novels_for_updates()
    mock_db_manager_for_scheduler.save_novel_metadata.assert_not_called()

@pytest.mark.asyncio
@patch('novel_notify.bot.scheduler.WebNovelScraper')
async def test_check_single_novel_no_metadata(MockScraperClass, update_scheduler, mock_db_manager_for_scheduler):
    mock_db_manager_for_scheduler.get_novel_metadata.return_value = None
    mock_instance = AsyncMock(spec=WebNovelScraper)
    MockScraperClass.return_value = mock_instance
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.quick_check_latest_chapter = AsyncMock()
    mock_db_manager_for_scheduler.get_all_subscriptions.return_value = [UserSubscription(user_id=TEST_USER_ID_SCHED_1, novel_id=TEST_NOVEL_ID_SCHED_1)]
    await update_scheduler.check_all_novels_for_updates()
    mock_instance.quick_check_latest_chapter.assert_not_called()

@pytest.mark.asyncio
async def test_notify_subscribers_no_subscribers(update_scheduler, mock_db_manager_for_scheduler, mock_bot_for_scheduler):
    mock_db_manager_for_scheduler.get_novel_subscribers.return_value = []
    await update_scheduler._notify_subscribers(TEST_NOVEL_ID_SCHED_1, METADATA_SCHED_1, UPDATED_CHAPTER_1)
    mock_bot_for_scheduler.send_message.assert_not_called()

@pytest.mark.asyncio
async def test_notify_subscribers_fails_to_send_one_message(update_scheduler, mock_db_manager_for_scheduler, mock_bot_for_scheduler):
    mock_db_manager_for_scheduler.get_novel_subscribers.return_value = [TEST_USER_ID_SCHED_1, TEST_USER_ID_SCHED_2]
    mock_bot_for_scheduler.send_message.side_effect = [AsyncMock(), Exception("Telegram API error")]
    await update_scheduler._notify_subscribers(TEST_NOVEL_ID_SCHED_1, METADATA_SCHED_1, UPDATED_CHAPTER_1)
    mock_db_manager_for_scheduler.update_last_notified_chapter.assert_called_once_with(TEST_USER_ID_SCHED_1, TEST_NOVEL_ID_SCHED_1, UPDATED_CHAPTER_1.title)

@pytest.mark.asyncio
@patch('novel_notify.bot.scheduler.WebNovelScraper')
async def test_manual_check_novel_success(MockScraperClass, update_scheduler, mock_db_manager_for_scheduler):
    mock_db_manager_for_scheduler.get_novel_metadata.return_value = METADATA_SCHED_1
    mock_instance = AsyncMock(spec=WebNovelScraper)
    MockScraperClass.return_value = mock_instance
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.quick_check_latest_chapter = AsyncMock(return_value=UPDATED_CHAPTER_1)
    mock_db_manager_for_scheduler.get_novel_subscribers.return_value = [TEST_USER_ID_SCHED_1]
    result = await update_scheduler.manual_check_novel(TEST_NOVEL_ID_SCHED_1)
    assert result is True

@pytest.mark.asyncio
@patch('novel_notify.bot.scheduler.WebNovelScraper')
async def test_manual_check_novel_exception(MockScraperClass, update_scheduler, mock_db_manager_for_scheduler):
    # Setup database mock to return metadata (needed for the check to proceed)
    mock_db_manager_for_scheduler.get_novel_metadata.return_value = METADATA_SCHED_1
    
    mock_instance = AsyncMock(spec=WebNovelScraper)
    MockScraperClass.return_value = mock_instance
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=None)
    mock_instance.quick_check_latest_chapter = AsyncMock(side_effect=Exception("Scraper network error"))
    result = await update_scheduler.manual_check_novel(TEST_NOVEL_ID_SCHED_1)
    assert result is False
