"""
Main entry point for the Novel Notify bot
"""

import logging
import asyncio
import signal
import sys
from typing import Optional

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters

from .config import config
from .database import DatabaseManager
from .bot import BotHandlers, UpdateScheduler
from .bot.handlers import WAITING_FOR_URL

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('novel_notify.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
app: Optional[Application] = None
scheduler: Optional[UpdateScheduler] = None


async def error_handler(update: object, context) -> None:
    """
    Handle errors in the bot
    
    Args:
        update: The update that caused the error
        context: Bot context containing error information
    """
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to notify user if update is available
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again later."
            )
        except Exception:
            pass


def signal_handler(signum, frame):
    """
    Handle shutdown signals
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    
    # Create new event loop for shutdown if current one is closed
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run shutdown coroutine
    loop.run_until_complete(shutdown())
    sys.exit(0)


async def shutdown():
    """Graceful shutdown of the bot"""
    global app, scheduler
    
    logger.info("Starting graceful shutdown...")
    
    try:
        if scheduler:
            scheduler.shutdown()
            logger.info("Scheduler stopped")
        
        if app:
            await app.stop()
            await app.shutdown()
            logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Shutdown complete")


async def main():
    """Main function to run the bot"""
    global app, scheduler
    
    try:
        logger.info("Starting Novel Notify Bot...")
        
        # Initialize database
        db_manager = DatabaseManager()
        logger.info("Database initialized")
        
        # Create bot application
        app = Application.builder().token(config.telegram_bot_token).build()
        
        # Initialize handlers
        handlers = BotHandlers(db_manager)
        
        # Initialize scheduler
        scheduler = UpdateScheduler(db_manager, app.bot)
        
        # Add command handlers
        app.add_handler(CommandHandler("start", handlers.start_command))
        app.add_handler(CommandHandler("help", handlers.help_command))
        app.add_handler(CommandHandler("list", handlers.list_novels_command))
        app.add_handler(CommandHandler("remove", handlers.remove_novel_command))
        app.add_handler(CommandHandler("check", handlers.check_updates_command))
        
        # Add conversation handler for adding novels
        add_novel_conversation = ConversationHandler(
            entry_points=[CommandHandler("add", handlers.add_novel_command)],
            states={
                WAITING_FOR_URL: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_url)
                ]
            },
            fallbacks=[CommandHandler("cancel", handlers.cancel_conversation)]
        )
        app.add_handler(add_novel_conversation)
        
        # Add handler for direct URL messages
        app.add_handler(MessageHandler(
            filters.TEXT & filters.Regex(r'webnovel\.com/book/') & ~filters.COMMAND,
            handlers.handle_url_message
        ))
        
        # Add error handler
        app.add_error_handler(error_handler)
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start scheduler
        scheduler.start()
        logger.info("Scheduler started")
        
        # Start bot
        logger.info("Bot starting...")
        await app.initialize()
        
        # Register bot commands
        commands = [
            BotCommand("start", "Start the bot and get welcome message"),
            BotCommand("help", "Show help message with available commands"),
            BotCommand("add", "Add a new novel to track"),
            BotCommand("list", "List all your tracked novels"),
            BotCommand("remove", "Remove a novel from tracking"),
            BotCommand("check", "Check for updates on your tracked novels"),
            BotCommand("cancel", "Cancel current operation")
        ]
        await app.bot.set_my_commands(commands)
        logger.info("Bot commands registered")
        
        await app.start()
        await app.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
        logger.info("Bot is running! Press Ctrl+C to stop.")
        
        # Keep the bot running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
    finally:
        await shutdown()


def run():
    """Entry point for the bot"""
    try:
        # Handle Python 3.10+ asyncio changes
        if sys.version_info >= (3, 10):
            # For Python 3.10+, we need to be more explicit about event loops
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
