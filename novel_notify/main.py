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
shutdown_event = asyncio.Event()


async def error_handler(update: object, context) -> None:
    """
    Handle errors in the bot
    
    Args:
        update: The update that caused the error
        context: Bot context containing error information
    """
    error = context.error
    
    # Don't log network errors that occur during shutdown
    if "httpx.ReadError" in str(error) or "NetworkError" in str(error):
        logger.debug(f"Network error (likely during shutdown): {error}")
        return
    
    logger.error(f"Exception while handling an update: {error}")
    
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
    
    # Signal the event loop to shutdown gracefully
    # Don't try to run coroutines from signal handler
    try:
        shutdown_event.set()
    except Exception as e:
        logger.error(f"Error setting shutdown event: {e}")
        # Force exit if we can't set the event
        sys.exit(1)


async def shutdown():
    """Graceful shutdown of the bot"""
    global app, scheduler
    
    logger.info("Starting graceful shutdown...")
    
    try:
        if scheduler:
            scheduler.shutdown()
            logger.info("Scheduler stopped")
        
        if app:
            # Stop updater first
            try:
                await app.updater.stop()
                logger.info("Updater stopped")
            except Exception as e:
                logger.warning(f"Error stopping updater: {e}")
            
            # Then stop the application
            try:
                await app.stop()
                logger.info("Application stopped")
            except Exception as e:
                logger.warning(f"Error stopping application: {e}")
            
            # Finally shutdown the application
            try:
                await app.shutdown()
                logger.info("Application shutdown complete")
            except Exception as e:
                logger.warning(f"Error during application shutdown: {e}")
                
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    # Give a moment for any remaining tasks to finish
    try:
        await asyncio.sleep(0.1)
    except Exception:
        pass
    
    logger.info("Shutdown complete")


async def main():
    """Main function to run the bot"""
    global app, scheduler, shutdown_event
    
    # Initialize shutdown event
    shutdown_event = asyncio.Event()
    
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
        
        # Wait for shutdown event instead of infinite loop
        try:
            await shutdown_event.wait()
            logger.info("Shutdown event received")
        except Exception as e:
            logger.error(f"Error waiting for shutdown event: {e}")
            
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
        
        # Run the main coroutine
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cancel any remaining tasks
        try:
            # Get the current event loop
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                # Cancel all remaining tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                
                # Give tasks a moment to cancel
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            # Ignore errors during cleanup
            pass


if __name__ == "__main__":
    run()
