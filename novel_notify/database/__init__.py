"""
Database manager for the Novel Notify bot
"""

import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import time

from .models import NovelMetadata, UserSubscription, Chapter
from ..config import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or config.database_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create novels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS novels (
                    novel_id TEXT PRIMARY KEY,
                    metadata TEXT NOT NULL,
                    last_updated REAL NOT NULL,
                    created_at REAL NOT NULL
                )
            ''')
            
            # Create subscriptions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    novel_id TEXT NOT NULL,
                    added_at REAL NOT NULL,
                    last_notified_chapter TEXT,
                    notifications_enabled BOOLEAN DEFAULT 1,
                    UNIQUE(user_id, novel_id),
                    FOREIGN KEY (novel_id) REFERENCES novels (novel_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_novel_id ON subscriptions(novel_id)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_novel_metadata(self, metadata: NovelMetadata) -> bool:
        """
        Save or update novel metadata
        
        Args:
            metadata: Novel metadata to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                metadata_json = json.dumps(metadata.to_dict())
                current_time = time.time()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO novels (novel_id, metadata, last_updated, created_at)
                    VALUES (?, ?, ?, COALESCE((SELECT created_at FROM novels WHERE novel_id = ?), ?))
                ''', (metadata.novel_id, metadata_json, current_time, metadata.novel_id, current_time))
                
                conn.commit()
                logger.info(f"Saved metadata for novel {metadata.novel_id}: {metadata.novel_title}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save novel metadata for {metadata.novel_id}: {e}")
            return False
    
    def get_novel_metadata(self, novel_id: str) -> Optional[NovelMetadata]:
        """
        Get novel metadata by ID
        
        Args:
            novel_id: Novel ID
            
        Returns:
            Novel metadata if found, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT metadata FROM novels WHERE novel_id = ?', (novel_id,))
                row = cursor.fetchone()
                
                if row:
                    metadata_dict = json.loads(row['metadata'])
                    return NovelMetadata.from_dict(metadata_dict)
                return None
                
        except Exception as e:
            logger.error(f"Failed to get novel metadata for {novel_id}: {e}")
            return None
    
    def get_all_novels(self) -> List[NovelMetadata]:
        """
        Get all stored novel metadata
        
        Returns:
            List of all novel metadata
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT metadata FROM novels ORDER BY last_updated DESC')
                rows = cursor.fetchall()
                
                novels = []
                for row in rows:
                    metadata_dict = json.loads(row['metadata'])
                    novels.append(NovelMetadata.from_dict(metadata_dict))
                
                return novels
                
        except Exception as e:
            logger.error(f"Failed to get all novels: {e}")
            return []
    
    def add_subscription(self, user_id: int, novel_id: str) -> bool:
        """
        Add a user subscription to a novel
        
        Args:
            user_id: Telegram user ID
            novel_id: Novel ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO subscriptions (user_id, novel_id, added_at)
                    VALUES (?, ?, ?)
                ''', (user_id, novel_id, time.time()))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Added subscription for user {user_id} to novel {novel_id}")
                    return True
                else:
                    logger.info(f"Subscription already exists for user {user_id} to novel {novel_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to add subscription for user {user_id} to novel {novel_id}: {e}")
            return False
    
    def remove_subscription(self, user_id: int, novel_id: str) -> bool:
        """
        Remove a user subscription
        
        Args:
            user_id: Telegram user ID
            novel_id: Novel ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM subscriptions WHERE user_id = ? AND novel_id = ?
                ''', (user_id, novel_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Removed subscription for user {user_id} from novel {novel_id}")
                    return True
                else:
                    logger.info(f"No subscription found for user {user_id} to novel {novel_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to remove subscription for user {user_id} from novel {novel_id}: {e}")
            return False
    
    def get_user_subscriptions(self, user_id: int) -> List[UserSubscription]:
        """
        Get all subscriptions for a user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of user subscriptions
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, novel_id, added_at, last_notified_chapter, notifications_enabled
                    FROM subscriptions WHERE user_id = ?
                    ORDER BY added_at DESC
                ''', (user_id,))
                rows = cursor.fetchall()
                
                subscriptions = []
                for row in rows:
                    subscription = UserSubscription(
                        user_id=row['user_id'],
                        novel_id=row['novel_id'],
                        added_at=row['added_at'],
                        last_notified_chapter=row['last_notified_chapter'],
                        notifications_enabled=bool(row['notifications_enabled'])
                    )
                    subscriptions.append(subscription)
                
                return subscriptions
                
        except Exception as e:
            logger.error(f"Failed to get subscriptions for user {user_id}: {e}")
            return []
    
    def get_novel_subscribers(self, novel_id: str) -> List[int]:
        """
        Get all user IDs subscribed to a novel
        
        Args:
            novel_id: Novel ID
            
        Returns:
            List of user IDs
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id FROM subscriptions 
                    WHERE novel_id = ? AND notifications_enabled = 1
                ''', (novel_id,))
                rows = cursor.fetchall()
                
                return [row['user_id'] for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get subscribers for novel {novel_id}: {e}")
            return []
    
    def update_last_notified_chapter(self, user_id: int, novel_id: str, chapter_title: str) -> bool:
        """
        Update the last notified chapter for a user subscription
        
        Args:
            user_id: Telegram user ID
            novel_id: Novel ID
            chapter_title: Chapter title
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE subscriptions 
                    SET last_notified_chapter = ?
                    WHERE user_id = ? AND novel_id = ?
                ''', (chapter_title, user_id, novel_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to update last notified chapter for user {user_id}, novel {novel_id}: {e}")
            return False
    
    def get_all_subscriptions(self) -> List[UserSubscription]:
        """
        Get all subscriptions in the database
        
        Returns:
            List of all subscriptions
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, novel_id, added_at, last_notified_chapter, notifications_enabled
                    FROM subscriptions
                    ORDER BY added_at DESC
                ''')
                rows = cursor.fetchall()
                
                subscriptions = []
                for row in rows:
                    subscription = UserSubscription(
                        user_id=row['user_id'],
                        novel_id=row['novel_id'],
                        added_at=row['added_at'],
                        last_notified_chapter=row['last_notified_chapter'],
                        notifications_enabled=bool(row['notifications_enabled'])
                    )
                    subscriptions.append(subscription)
                
                return subscriptions
                
        except Exception as e:
            logger.error(f"Failed to get all subscriptions: {e}")
            return []
