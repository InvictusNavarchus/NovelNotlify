import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from telegram import Update, User, Message, Chat
from telegram.ext import Application, ContextTypes, ApplicationBuilder

from novel_notify.database import DatabaseManager
from novel_notify.bot.handlers import BotHandlers
from novel_notify.config import Config

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for our test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session") # Changed to session scope for wider use if needed
def mock_config_values():
    """Provides a dictionary of mock config values."""
    return {
        "telegram_bot_token": "test_token_from_mock",
        "check_interval": 1800, # Using a different value to ensure mock is used
        "database_path": ":memory:",
        "cors_proxy_url": "http://mock-cors.test/",
        "webnovel_base_url": "https://mock.webnovel.com",
        "log_level": "DEBUG"
    }

@pytest.fixture(autouse=True) # Autouse to apply to all tests
def mock_config_object(mocker, mock_config_values):
    """
    Mocks the novel_notify.config.config object for all tests.
    This prevents the actual Config class from trying to load .env files.
    """
    mocked_config_instance = MagicMock(spec=Config)

    # Set attributes on the mock instance using values from mock_config_values
    for key, value in mock_config_values.items():
        setattr(mocked_config_instance, key, value)

    # Patch the '_instance' attribute of the ConfigProxy class.
    # This ensures that when 'config.ANY_ATTRIBUTE' is first accessed in app code,
    # it will use our mocked_config_instance instead of creating a new Config().
    mocker.patch('novel_notify.config.ConfigProxy._instance', mocked_config_instance)

    # Additionally, to be absolutely sure, if any module imports 'config' directly and
    # the test execution order causes it to be accessed before ConfigProxy._instance is patched,
    # we can also patch the 'config' object in those modules.
    # However, patching ConfigProxy._instance should be the primary mechanism.
    # The direct patches below act as a safeguard or for modules that might somehow bypass the proxy.
    # For most cases, patching ConfigProxy._instance should be sufficient.
    mocker.patch('novel_notify.database.config', mocked_config_instance)
    mocker.patch('novel_notify.scraper.config', mocked_config_instance)
    mocker.patch('novel_notify.bot.scheduler.config', mocked_config_instance)
    # mocker.patch('novel_notify.main.config', mocked_config_instance) # If main.py also uses it

    return mocked_config_instance


@pytest.fixture
async def mock_application(mock_config_object): # Depends on the mocked config
    """Fixture for a mock Application object."""
    application = ApplicationBuilder().token(mock_config_object.telegram_bot_token).build()
    application.bot = AsyncMock()
    return application

@pytest.fixture
def mock_db_manager(mock_config_object): # Depends on the mocked config
    """Fixture for a mock DatabaseManager."""
    # Use in-memory SQLite database for tests, configured by the mocked config
    db_manager = DatabaseManager(db_path=mock_config_object.database_path)
    return db_manager

@pytest.fixture
def bot_handlers(mock_db_manager):
    """Fixture for BotHandlers with a mock DatabaseManager."""
    return BotHandlers(db_manager=mock_db_manager)

@pytest.fixture
def mock_update():
    """Fixture for a mock Update object."""
    update = MagicMock(spec=Update)
    update.effective_user = User(id=123, first_name="Test", is_bot=False)
    update.message = MagicMock(spec=Message)
    update.message.chat = Chat(id=123, type="private")
    update.message.reply_text = AsyncMock()
    update.message.reply_markdown = AsyncMock() # if you use reply_markdown
    update.callback_query = None # Or MagicMock() if you test callback queries
    return update

@pytest.fixture
def mock_context(mock_application):
    """Fixture for a mock ContextTypes.DEFAULT_TYPE object."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = mock_application.bot
    context.args = []
    # context.user_data = {} # If you use user_data
    # context.chat_data = {} # If you use chat_data
    # context.application = mock_application # If needed
    return context

# You can add more specific mock objects or helper functions here as needed.
# For example, mock WebNovelScraper:

@pytest.fixture
def mock_scraper():
    """Fixture for a mock WebNovelScraper."""
    scraper = AsyncMock()
    # Define return values for its methods, e.g.:
    # scraper.scrape_novel_metadata.return_value = ...
    # scraper.quick_check_latest_chapter.return_value = ...
    return scraper
