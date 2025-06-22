"""
Background scheduler for checking novel updates
"""

import asyncio
import logging
from typing import List
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..database import DatabaseManager
from ..database.models import UserSubscription
from ..scraper import WebNovelScraper
from ..config import config

logger = logging.getLogger(__name__)


class UpdateScheduler:
    """Handles scheduled checking of novel updates"""
    
    def __init__(self, db_manager: DatabaseManager, bot):
        """
        Initialize update scheduler
        
        Args:
            db_manager: Database manager instance
            bot: Telegram bot instance
        """
        self.db = db_manager
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs"""
        # Schedule update checking
        self.scheduler.add_job(
            self.check_all_novels_for_updates,
            trigger=IntervalTrigger(seconds=config.check_interval),
            id='check_updates',
            name='Check Novel Updates',
            max_instances=1,
            coalesce=True
        )
        
        logger.info(f"Scheduled update checking every {config.check_interval} seconds")
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Update scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown(wait=False)
        logger.info("Update scheduler shutdown")
    
    async def check_all_novels_for_updates(self):
        """
        Check all tracked novels for updates and notify users
        """
        logger.info("Starting scheduled update check")
        
        try:
            # Get all unique novels that are being tracked
            all_subscriptions = self.db.get_all_subscriptions()
            unique_novels = list(set(sub.novel_id for sub in all_subscriptions))
            
            if not unique_novels:
                logger.info("No novels to check")
                return
            
            logger.info(f"Checking {len(unique_novels)} novels for updates")
            
            async with WebNovelScraper() as scraper:
                for novel_id in unique_novels:
                    try:
                        await self._check_single_novel(scraper, novel_id)
                        # Small delay to avoid rate limiting
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.error(f"Error checking novel {novel_id}: {e}")
                        continue
            
            logger.info("Scheduled update check completed")
            
        except Exception as e:
            logger.error(f"Error in scheduled update check: {e}")
    
    async def _check_single_novel(self, scraper: WebNovelScraper, novel_id: str):
        """
        Check a single novel for updates
        
        Args:
            scraper: WebNovel scraper instance
            novel_id: Novel ID to check
        """
        try:
            # Get current metadata
            current_metadata = self.db.get_novel_metadata(novel_id)
            if not current_metadata:
                logger.warning(f"No metadata found for novel {novel_id}")
                return
            
            # Compare latest chapter with last free chapter
            comparison = await scraper.compare_latest_chapters(novel_id)
            if not comparison['latest_chapter']:
                logger.warning(f"Could not fetch latest chapter for novel {novel_id}")
                return
            
            latest_chapter = comparison['latest_chapter']
            last_free_chapter = comparison['last_free_chapter']
            has_paid_chapters = comparison['has_paid_chapters']
            
            # Always update the last_updated timestamp to show when we last checked
            current_metadata.last_updated = time.time()
            
            # Determine which chapter to use for comparison and notification
            # We prioritize free chapters for notifications
            chapter_for_notification = last_free_chapter if last_free_chapter else latest_chapter
            
            # Check if there's an update
            if chapter_for_notification.title == current_metadata.latest_chapter.title:
                # No update found, but save the updated timestamp
                self.db.save_novel_metadata(current_metadata)
                return
            
            logger.info(f"Update found for novel {current_metadata.novel_title}: {chapter_for_notification.title}")
            
            if has_paid_chapters and last_free_chapter:
                logger.info(f"Novel has paid chapters. Latest: {latest_chapter.title}, Last Free: {last_free_chapter.title}")
            
            # Update metadata with new chapter (use the one for notification)
            current_metadata.latest_chapter = chapter_for_notification
            self.db.save_novel_metadata(current_metadata)
            
            # Notify subscribers
            await self._notify_subscribers(novel_id, current_metadata, chapter_for_notification, has_paid_chapters)
            
        except Exception as e:
            logger.error(f"Error checking single novel {novel_id}: {e}")
    
    async def _notify_subscribers(self, novel_id: str, metadata, new_chapter, has_paid_chapters: bool = False):
        """
        Notify all subscribers of a novel about the new chapter
        
        Args:
            novel_id: Novel ID
            metadata: Novel metadata
            new_chapter: New chapter information
            has_paid_chapters: Whether the novel has paid chapters
        """
        try:
            # Get all subscribers for this novel
            subscriber_ids = self.db.get_novel_subscribers(novel_id)
            
            if not subscriber_ids:
                return
            
            logger.info(f"Notifying {len(subscriber_ids)} subscribers about update for {metadata.novel_title}")
            
            # Prepare notification message
            chapter_type = "🆓 Free" if not new_chapter.is_locked else "🔐 Paid"
            paid_chapters_note = "\n\n⚠️ *Note: This novel has paid chapters. This notification is for the latest free chapter.*" if has_paid_chapters else ""
            
            notification_message = f"""
🆕 **New Chapter Available!**

📖 **{metadata.novel_title}**
✍️ Author: {metadata.author}

📚 **Latest {chapter_type} Chapter:**
{new_chapter.title}

🔗 [Read Now](https://www.webnovel.com/book/{novel_id})

🕒 Published: {new_chapter.published}{paid_chapters_note}
            """
            
            # Send notifications to all subscribers
            successful_notifications = 0
            for user_id in subscriber_ids:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=notification_message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    
                    # Update last notified chapter
                    self.db.update_last_notified_chapter(user_id, novel_id, new_chapter.title)
                    successful_notifications += 1
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Failed to notify user {user_id} about novel {novel_id}: {e}")
                    continue
            
            logger.info(f"Successfully notified {successful_notifications}/{len(subscriber_ids)} subscribers")
            
        except Exception as e:
            logger.error(f"Error notifying subscribers for novel {novel_id}: {e}")
    
    async def manual_check_novel(self, novel_id: str) -> bool:
        """
        Manually check a specific novel for updates
        
        Args:
            novel_id: Novel ID to check
            
        Returns:
            True if update found, False otherwise
        """
        try:
            async with WebNovelScraper() as scraper:
                await self._check_single_novel(scraper, novel_id)
                return True
        except Exception as e:
            logger.error(f"Error in manual novel check for {novel_id}: {e}")
            return False
