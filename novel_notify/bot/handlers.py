"""
Telegram bot handlers for the Novel Notify bot
"""

import logging
from typing import List, Optional
import asyncio
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from ..database import DatabaseManager
from ..database.models import NovelMetadata, UserSubscription
from ..scraper import WebNovelScraper
from ..utils import extract_novel_id_from_url, format_novel_url, format_time_ago, truncate_text, format_published_time

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_URL = 1


class BotHandlers:
    """Telegram bot command and message handlers"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize bot handlers
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        user = update.effective_user
        welcome_message = f"""
🔥 **Welcome to Novel Notify Bot!** 🔥

Hello {user.first_name}! I help you track your favorite WebNovel stories and notify you when new chapters are released.

**What I can do:**
📚 Track novels from WebNovel URLs
🔔 Send notifications for new chapters
📊 Show your tracked novels and updates
⚡ Check for updates on demand

**Quick Start:**
1. Send me a WebNovel URL (e.g., https://www.webnovel.com/book/12345)
2. I'll add it to your tracking list
3. Sit back and get notified when new chapters arrive!

**Available Commands:**
/help - Show all commands
/add - Add a novel to track
/list - Show your tracked novels
/check - Check for updates
/remove - Remove a novel from tracking

**Ready to start?** Just send me a WebNovel URL! 🚀
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /help command
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        help_message = """
📖 **Novel Notify Bot Commands**

**Basic Commands:**
/start - Show welcome message
/help - Show this help message

**Novel Management:**
/add `<url>` - Add a novel to track
/list - Show your tracked novels
/remove `<number>` - Remove novel by list number
/check - Check for updates on all tracked novels

**Quick Actions:**
Just send me a WebNovel URL and I'll add it automatically!

**Supported URL Formats:**
• https://www.webnovel.com/book/title_12345
• https://www.webnovel.com/book/12345

**Examples:**
/add https://www.webnovel.com/book/12345
/remove 1

**Tips:**
🔔 Notifications are enabled by default
⏰ I check for updates every hour
📊 Use /check to get instant updates
🚫 Use /remove to stop tracking a novel

Need more help? Just ask! 😊
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def add_novel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handle /add command
        
        Args:
            update: Telegram update object
            context: Bot context
            
        Returns:
            Conversation state
        """
        if context.args:
            # URL provided with command
            url = ' '.join(context.args)
            await self._process_novel_url(update, context, url)
            return ConversationHandler.END
        else:
            # Ask for URL
            await update.message.reply_text(
                "📚 **Add a Novel**\n\n"
                "Please send me the WebNovel URL you want to track.\n"
                "Example: https://www.webnovel.com/book/12345\n\n"
                "Or type /cancel to cancel.",
                parse_mode=ParseMode.MARKDOWN
            )
            return WAITING_FOR_URL
    
    async def receive_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Handle URL input during conversation
        
        Args:
            update: Telegram update object
            context: Bot context
            
        Returns:
            Conversation state
        """
        url = update.message.text.strip()
        await self._process_novel_url(update, context, url)
        return ConversationHandler.END
    
    async def cancel_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Cancel conversation
        
        Args:
            update: Telegram update object
            context: Bot context
            
        Returns:
            Conversation state
        """
        await update.message.reply_text(
            "❌ Operation cancelled.",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    async def _process_novel_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str) -> None:
        """
        Process a novel URL and add it to tracking
        
        Args:
            update: Telegram update object
            context: Bot context
            url: Novel URL to process
        """
        user_id = update.effective_user.id
        
        # Extract novel ID from URL
        novel_id = extract_novel_id_from_url(url)
        if not novel_id:
            await update.message.reply_text(
                "❌ **Invalid URL**\n\n"
                "Please provide a valid WebNovel URL.\n"
                "Example: https://www.webnovel.com/book/12345",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check if already subscribed
        existing_subscriptions = self.db.get_user_subscriptions(user_id)
        if any(sub.novel_id == novel_id for sub in existing_subscriptions):
            await update.message.reply_text(
                "📚 **Already Tracking**\n\n"
                "You're already tracking this novel!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🔄 **Processing...**\n\n"
            "Fetching novel information from WebNovel...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Scrape novel metadata
            async with WebNovelScraper() as scraper:
                metadata = await scraper.scrape_novel_metadata(novel_id)
            
            if not metadata:
                await processing_msg.edit_text(
                    "❌ **Failed to Fetch Novel**\n\n"
                    "Could not retrieve novel information. Please check the URL and try again.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Save to database
            if not self.db.save_novel_metadata(metadata):
                await processing_msg.edit_text(
                    "❌ **Database Error**\n\n"
                    "Failed to save novel information. Please try again later.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Add subscription
            if not self.db.add_subscription(user_id, novel_id):
                await processing_msg.edit_text(
                    "❌ **Subscription Error**\n\n"
                    "Failed to add novel to your tracking list. Please try again later.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Success message
            success_message = f"""
✅ **Novel Added Successfully!**

📖 **{metadata.novel_title}**
✍️ Author: {metadata.author}
📚 Latest: {metadata.latest_chapter.title}
� Published: {metadata.latest_chapter.published}
�🔔 Notifications: Enabled

I'll notify you when new chapters are released!
            """
            
            await processing_msg.edit_text(
                success_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error processing novel URL {url}: {e}")
            await processing_msg.edit_text(
                "❌ **Error**\n\n"
                "An unexpected error occurred. Please try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def list_novels_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /list command
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        user_id = update.effective_user.id
        subscriptions = self.db.get_user_subscriptions(user_id)
        
        if not subscriptions:
            await update.message.reply_text(
                "📚 **No Novels Tracked**\n\n"
                "You're not tracking any novels yet.\n"
                "Send me a WebNovel URL to get started!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        message_parts = ["📚 **Your Tracked Novels**\n"]
        
        for i, subscription in enumerate(subscriptions, 1):
            metadata = self.db.get_novel_metadata(subscription.novel_id)
            if metadata:
                status = "🔔" if subscription.notifications_enabled else "🔕"
                time_ago = format_time_ago(metadata.last_updated)
                
                novel_info = f"""
**{i}.** {status} **{truncate_text(metadata.novel_title, 40)}**
✍️ {metadata.author}
📚 {metadata.latest_chapter.title}
� Published: {metadata.latest_chapter.published}
�🕒 Updated {time_ago}
"""
                message_parts.append(novel_info)
        
        message_parts.append(f"\n📊 **Total:** {len(subscriptions)} novels")
        message_parts.append("🗑️ Use `/remove <number>` to stop tracking")
        
        full_message = '\n'.join(message_parts)
        
        # Split message if too long
        if len(full_message) > 4000:
            # Send in chunks
            current_message = "📚 **Your Tracked Novels**\n"
            for i, subscription in enumerate(subscriptions, 1):
                metadata = self.db.get_novel_metadata(subscription.novel_id)
                if metadata:
                    status = "🔔" if subscription.notifications_enabled else "🔕"
                    novel_info = f"**{i}.** {status} {truncate_text(metadata.novel_title, 30)}\n"
                    
                    if len(current_message + novel_info) > 4000:
                        await update.message.reply_text(current_message, parse_mode=ParseMode.MARKDOWN)
                        current_message = novel_info
                    else:
                        current_message += novel_info
            
            if current_message:
                current_message += f"\n📊 **Total:** {len(subscriptions)} novels"
                await update.message.reply_text(current_message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(full_message, parse_mode=ParseMode.MARKDOWN)
    
    async def remove_novel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /remove command
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "🗑️ **Remove a Novel**\n\n"
                "Usage: `/remove <number>`\n"
                "Example: `/remove 1`\n\n"
                "Use /list to see your novels with numbers.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            novel_number = int(context.args[0])
        except (ValueError, IndexError):
            await update.message.reply_text(
                "❌ **Invalid Number**\n\n"
                "Please provide a valid number.\n"
                "Use /list to see your novels with numbers.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        subscriptions = self.db.get_user_subscriptions(user_id)
        
        if novel_number < 1 or novel_number > len(subscriptions):
            await update.message.reply_text(
                f"❌ **Invalid Number**\n\n"
                f"Please choose a number between 1 and {len(subscriptions)}.\n"
                "Use /list to see your novels.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get the subscription to remove
        subscription = subscriptions[novel_number - 1]
        metadata = self.db.get_novel_metadata(subscription.novel_id)
        
        # Remove subscription
        if self.db.remove_subscription(user_id, subscription.novel_id):
            novel_title = metadata.novel_title if metadata else "Unknown Novel"
            await update.message.reply_text(
                f"✅ **Novel Removed**\n\n"
                f"Stopped tracking: **{novel_title}**\n"
                f"You'll no longer receive notifications for this novel.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ **Error**\n\n"
                "Failed to remove novel. Please try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def check_updates_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /check command
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        user_id = update.effective_user.id
        subscriptions = self.db.get_user_subscriptions(user_id)
        
        if not subscriptions:
            await update.message.reply_text(
                "📚 **No Novels to Check**\n\n"
                "You're not tracking any novels yet.\n"
                "Send me a WebNovel URL to get started!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        processing_msg = await update.message.reply_text(
            f"🔄 **Checking Updates...**\n\n"
            f"Checking {len(subscriptions)} novels for updates...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            updates_found = []
            async with WebNovelScraper() as scraper:
                for subscription in subscriptions:
                    try:
                        # Get current metadata
                        current_metadata = self.db.get_novel_metadata(subscription.novel_id)
                        if not current_metadata:
                            continue
                        
                        # Quick check for latest chapter
                        latest_chapter = await scraper.quick_check_latest_chapter(subscription.novel_id)
                        if not latest_chapter:
                            continue
                        
                        # Check if there's an update
                        if latest_chapter.title != current_metadata.latest_chapter.title:
                            # Update metadata
                            current_metadata.latest_chapter = latest_chapter
                            current_metadata.last_updated = time.time()
                            self.db.save_novel_metadata(current_metadata)
                            
                            updates_found.append({
                                'title': current_metadata.novel_title,
                                'chapter': latest_chapter.title,
                                'url': format_novel_url(subscription.novel_id),
                                'published': latest_chapter.published
                            })
                        
                        # Small delay to avoid rate limiting
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error checking updates for novel {subscription.novel_id}: {e}")
                        continue
            
            # Send results
            if updates_found:
                message_parts = ["🆕 **Updates Found!**\n"]
                for update_info in updates_found:
                    message_parts.append(
                        f"📖 **{update_info['title']}**\n"
                        f"📚 {update_info['chapter']}\n"
                        f"� Published: {update_info['published']}\n"
                        f"�🔗 [Read Now]({update_info['url']})\n"
                    )
                
                await processing_msg.edit_text(
                    '\n'.join(message_parts),
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
            else:
                await processing_msg.edit_text(
                    "📊 **Check Complete**\n\n"
                    "No new updates found for your tracked novels.\n"
                    "I'll notify you automatically when new chapters are released!",
                    parse_mode=ParseMode.MARKDOWN
                )
                
        except Exception as e:
            logger.error(f"Error checking updates: {e}")
            await processing_msg.edit_text(
                "❌ **Error**\n\n"
                "Failed to check for updates. Please try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_url_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle direct URL messages
        
        Args:
            update: Telegram update object
            context: Bot context
        """
        message_text = update.message.text.strip()
        
        # Check if message contains a WebNovel URL
        if 'webnovel.com/book/' in message_text:
            await self._process_novel_url(update, context, message_text)
        else:
            await update.message.reply_text(
                "🤔 **I don't understand**\n\n"
                "Send me a WebNovel URL to track a novel, or use /help to see available commands.",
                parse_mode=ParseMode.MARKDOWN
            )
