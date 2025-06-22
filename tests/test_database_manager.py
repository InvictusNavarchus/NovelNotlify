import pytest
import time
from unittest.mock import patch, MagicMock

from novel_notify.database import DatabaseManager
from novel_notify.database.models import NovelMetadata, Chapter

# Test data
TEST_NOVEL_ID_1 = "db_novel_1"
TEST_NOVEL_ID_2 = "db_novel_2"
TEST_USER_ID_1 = 1001
TEST_USER_ID_2 = 1002

SAMPLE_CHAPTER_1 = Chapter(
    chapter_number=1,
    title="DB Test Chapter 1",
    url="http://example.com/db_novel_1/ch1",
    published="2023-02-01 10:00:00"
)
SAMPLE_METADATA_1 = NovelMetadata(
    novel_id=TEST_NOVEL_ID_1,
    novel_title="DB Test Novel 1",
    author="DB Test Author 1",
    cover_url="http://example.com/cover1.jpg",
    latest_chapter=SAMPLE_CHAPTER_1,
    last_updated=time.time()
)

SAMPLE_CHAPTER_2 = Chapter(
    chapter_number=1,
    title="DB Test Chapter 1 - Novel 2",
    url="http://example.com/db_novel_2/ch1",
    published="2023-02-02 11:00:00"
)
SAMPLE_METADATA_2 = NovelMetadata(
    novel_id=TEST_NOVEL_ID_2,
    novel_title="DB Test Novel 2",
    author="DB Test Author 2",
    cover_url="http://example.com/cover2.jpg",
    latest_chapter=SAMPLE_CHAPTER_2,
    last_updated=time.time()
)


@pytest.fixture
def db_manager(tmp_path):
    """Fixture for a DatabaseManager using a temporary database file."""
    db_file = tmp_path / "test_novels.db"
    manager = DatabaseManager(db_path=str(db_file))
    # Ensure a clean state for each test if needed, though DatabaseManager typically creates tables if not exist
    # For true isolation, you could delete and recreate the db file or tables here.
    return manager

def test_database_initialization(tmp_path):
    """Test that the database and tables are created on initialization."""
    db_file = tmp_path / "init_test.db"
    assert not db_file.exists()
    manager = DatabaseManager(db_path=str(db_file))
    assert db_file.exists()

    # Check if tables were created
    with manager._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='novels';")
        assert cursor.fetchone() is not None
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscriptions';")
        assert cursor.fetchone() is not None

def test_save_and_get_novel_metadata(db_manager):
    """Test saving and retrieving novel metadata."""
    assert db_manager.save_novel_metadata(SAMPLE_METADATA_1)

    retrieved_metadata = db_manager.get_novel_metadata(TEST_NOVEL_ID_1)
    assert retrieved_metadata is not None
    assert retrieved_metadata.novel_id == SAMPLE_METADATA_1.novel_id
    assert retrieved_metadata.novel_title == SAMPLE_METADATA_1.novel_title
    assert retrieved_metadata.latest_chapter.title == SAMPLE_METADATA_1.latest_chapter.title

    # Test getting non-existent metadata
    assert db_manager.get_novel_metadata("non_existent_id") is None

def test_save_novel_metadata_updates_existing(db_manager):
    """Test that saving metadata for an existing novel updates it."""
    db_manager.save_novel_metadata(SAMPLE_METADATA_1)
    original_time = db_manager.get_novel_metadata(TEST_NOVEL_ID_1).last_updated

    time.sleep(0.01) # Ensure time difference for last_updated

    updated_chapter = Chapter(
        chapter_number=2,
        title="DB Test Chapter 2 - Updated",
        url="http://example.com/db_novel_1/ch2",
        published="2023-02-01 12:00:00"
    )
    updated_metadata = NovelMetadata(
        novel_id=TEST_NOVEL_ID_1,
        novel_title="DB Test Novel 1 - Updated Title", # Changed title
        author=SAMPLE_METADATA_1.author,
        cover_url=SAMPLE_METADATA_1.cover_url,
        latest_chapter=updated_chapter,
        last_updated=time.time() # This will be set by save_novel_metadata
    )
    assert db_manager.save_novel_metadata(updated_metadata)

    retrieved_metadata = db_manager.get_novel_metadata(TEST_NOVEL_ID_1)
    assert retrieved_metadata.novel_title == "DB Test Novel 1 - Updated Title"
    assert retrieved_metadata.latest_chapter.title == updated_chapter.title
    assert retrieved_metadata.last_updated > original_time

def test_get_all_novels(db_manager):
    """Test retrieving all novel metadata."""
    assert db_manager.get_all_novels() == [] # Initially empty

    db_manager.save_novel_metadata(SAMPLE_METADATA_1)
    db_manager.save_novel_metadata(SAMPLE_METADATA_2)

    all_novels = db_manager.get_all_novels()
    assert len(all_novels) == 2
    novel_ids = {n.novel_id for n in all_novels}
    assert TEST_NOVEL_ID_1 in novel_ids
    assert TEST_NOVEL_ID_2 in novel_ids

def test_add_and_get_user_subscriptions(db_manager):
    """Test adding and retrieving user subscriptions."""
    # Ensure novels exist before adding subscriptions
    db_manager.save_novel_metadata(SAMPLE_METADATA_1)
    db_manager.save_novel_metadata(SAMPLE_METADATA_2)

    assert db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_1)
    assert db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_2)
    assert db_manager.add_subscription(TEST_USER_ID_2, TEST_NOVEL_ID_1)

    # Test adding an existing subscription (should return False or be ignored)
    assert not db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_1)

    user1_subs = db_manager.get_user_subscriptions(TEST_USER_ID_1)
    assert len(user1_subs) == 2
    subscribed_novel_ids_user1 = {s.novel_id for s in user1_subs}
    assert TEST_NOVEL_ID_1 in subscribed_novel_ids_user1
    assert TEST_NOVEL_ID_2 in subscribed_novel_ids_user1

    user2_subs = db_manager.get_user_subscriptions(TEST_USER_ID_2)
    assert len(user2_subs) == 1
    assert user2_subs[0].novel_id == TEST_NOVEL_ID_1

    assert db_manager.get_user_subscriptions(9999) == [] # Non-existent user

def test_remove_subscription(db_manager):
    """Test removing a user subscription."""
    db_manager.save_novel_metadata(SAMPLE_METADATA_1)
    db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_1)

    assert len(db_manager.get_user_subscriptions(TEST_USER_ID_1)) == 1

    assert db_manager.remove_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_1)
    assert len(db_manager.get_user_subscriptions(TEST_USER_ID_1)) == 0

    # Test removing non-existent subscription
    assert not db_manager.remove_subscription(TEST_USER_ID_1, "non_existent_novel")
    assert not db_manager.remove_subscription(9999, TEST_NOVEL_ID_1)

def test_get_novel_subscribers(db_manager):
    """Test retrieving all users subscribed to a novel."""
    db_manager.save_novel_metadata(SAMPLE_METADATA_1)
    db_manager.save_novel_metadata(SAMPLE_METADATA_2)

    db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_1)
    db_manager.add_subscription(TEST_USER_ID_2, TEST_NOVEL_ID_1)
    db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_2) # User 1 also subscribed to novel 2

    subscribers_novel1 = db_manager.get_novel_subscribers(TEST_NOVEL_ID_1)
    assert len(subscribers_novel1) == 2
    assert TEST_USER_ID_1 in subscribers_novel1
    assert TEST_USER_ID_2 in subscribers_novel1

    subscribers_novel2 = db_manager.get_novel_subscribers(TEST_NOVEL_ID_2)
    assert len(subscribers_novel2) == 1
    assert TEST_USER_ID_1 in subscribers_novel2

    assert db_manager.get_novel_subscribers("non_existent_novel") == []

def test_update_last_notified_chapter(db_manager):
    """Test updating the last notified chapter for a subscription."""
    db_manager.save_novel_metadata(SAMPLE_METADATA_1)
    db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_1)

    new_chapter_title = "Chapter 2: The Adventure Continues"
    assert db_manager.update_last_notified_chapter(TEST_USER_ID_1, TEST_NOVEL_ID_1, new_chapter_title)

    subs = db_manager.get_user_subscriptions(TEST_USER_ID_1)
    assert subs[0].last_notified_chapter == new_chapter_title

    # Test updating non-existent subscription
    assert not db_manager.update_last_notified_chapter(9999, TEST_NOVEL_ID_1, "some_chapter")

def test_get_all_subscriptions(db_manager):
    """Test retrieving all subscriptions from the database."""
    assert db_manager.get_all_subscriptions() == [] # Initially empty

    db_manager.save_novel_metadata(SAMPLE_METADATA_1)
    db_manager.save_novel_metadata(SAMPLE_METADATA_2)

    db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_1)
    db_manager.add_subscription(TEST_USER_ID_2, TEST_NOVEL_ID_1)
    db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_2)

    all_subs = db_manager.get_all_subscriptions()
    assert len(all_subs) == 3

    # Check if one of the subscriptions is correct
    found_sub = False
    for sub in all_subs:
        if sub.user_id == TEST_USER_ID_1 and sub.novel_id == TEST_NOVEL_ID_2:
            found_sub = True
            break
    assert found_sub

# Test error handling (optional, but good for robustness)
@patch('sqlite3.connect')
def test_database_connection_error_on_init(mock_connect, tmp_path):
    """Test handling of connection error during DatabaseManager initialization."""
    db_file = tmp_path / "error_test.db"
    mock_connect.side_effect = Exception("Connection failed")
    with pytest.raises(Exception, match="Connection failed"):
        DatabaseManager(db_path=str(db_file))

@patch.object(DatabaseManager, '_get_connection')
def test_save_novel_metadata_handles_exception(mock_get_connection, db_manager):
    """Test that save_novel_metadata handles exceptions and returns False."""
    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = Exception("DB write error")
    mock_get_connection.return_value.__enter__.return_value = mock_conn

    assert not db_manager.save_novel_metadata(SAMPLE_METADATA_1)

@patch.object(DatabaseManager, '_get_connection')
def test_get_novel_metadata_handles_exception(mock_get_connection, db_manager):
    """Test that get_novel_metadata handles exceptions and returns None."""
    mock_conn = MagicMock()
    mock_conn.cursor.side_effect = Exception("DB read error")
    mock_get_connection.return_value.__enter__.return_value = mock_conn

    assert db_manager.get_novel_metadata(TEST_NOVEL_ID_1) is None

# Add similar exception handling tests for other methods if desired.
# e.g., add_subscription, remove_subscription etc.

def test_subscription_notifications_enabled_default_and_update(db_manager):
    """Test that notifications_enabled defaults to True and can be read."""
    db_manager.save_novel_metadata(SAMPLE_METADATA_1)
    db_manager.add_subscription(TEST_USER_ID_1, TEST_NOVEL_ID_1)

    subs = db_manager.get_user_subscriptions(TEST_USER_ID_1)
    assert len(subs) == 1
    assert subs[0].notifications_enabled is True

    # Test that get_novel_subscribers only returns users with notifications_enabled=True
    subscribers = db_manager.get_novel_subscribers(TEST_NOVEL_ID_1)
    assert TEST_USER_ID_1 in subscribers

    # Manually update notifications_enabled to False to test get_novel_subscribers
    with db_manager._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE subscriptions SET notifications_enabled = 0 WHERE user_id = ? AND novel_id = ?",
                       (TEST_USER_ID_1, TEST_NOVEL_ID_1))
        conn.commit()

    subs_after_update = db_manager.get_user_subscriptions(TEST_USER_ID_1)
    assert subs_after_update[0].notifications_enabled is False

    subscribers_after_disable = db_manager.get_novel_subscribers(TEST_NOVEL_ID_1)
    assert TEST_USER_ID_1 not in subscribers_after_disable
    assert len(subscribers_after_disable) == 0

    # Add another subscriber who should still be returned
    db_manager.add_subscription(TEST_USER_ID_2, TEST_NOVEL_ID_1)
    subscribers_with_new = db_manager.get_novel_subscribers(TEST_NOVEL_ID_1)
    assert TEST_USER_ID_2 in subscribers_with_new
    assert TEST_USER_ID_1 not in subscribers_with_new # Still disabled
    assert len(subscribers_with_new) == 1
