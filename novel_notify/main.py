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


def emergency_exit(signum, frame):
    """
    Emergency exit handler - forces termination if shutdown hangs
    
    Args:
        signum: Signal number  
        frame: Current stack frame
    """
    logger.critical("Emergency exit triggered - shutdown took too long, forcing termination")
    sys.exit(1)


async def shutdown():
    """Graceful shutdown of the bot with timeouts to prevent hanging"""
    global app, scheduler
    
    logger.info("Starting graceful shutdown...")
    shutdown_timeout = 30.0  # Total shutdown timeout in seconds
    operation_timeout = 10.0  # Timeout for individual operations
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Step 1: Stop scheduler (non-async, should be quick)
        if scheduler:
            try:
                scheduler.shutdown()
                logger.info("Scheduler stopped")
            except Exception as e:
                logger.warning(f"Error stopping scheduler: {e}")
        
        if app:
            # Step 2: Stop updater with timeout
            try:
                await asyncio.wait_for(app.updater.stop(), timeout=operation_timeout)
                logger.info("Updater stopped")
            except asyncio.TimeoutError:
                logger.warning(f"Updater stop timed out after {operation_timeout}s")
            except Exception as e:
                logger.warning(f"Error stopping updater: {e}")
            
            # Check if we still have time for remaining operations
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= shutdown_timeout:
                logger.warning("Shutdown timeout reached, forcing exit")
                return
            
            # Step 3: Stop application with timeout
            remaining_time = shutdown_timeout - elapsed
            app_timeout = min(operation_timeout, remaining_time)
            try:
                await asyncio.wait_for(app.stop(), timeout=app_timeout)
                logger.info("Application stopped")
            except asyncio.TimeoutError:
                logger.warning(f"Application stop timed out after {app_timeout}s")
            except Exception as e:
                logger.warning(f"Error stopping application: {e}")
            
            # Check if we still have time for final shutdown
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= shutdown_timeout:
                logger.warning("Shutdown timeout reached, forcing exit")
                return
            
            # Step 4: Final application shutdown with timeout
            remaining_time = shutdown_timeout - elapsed
            final_timeout = min(operation_timeout, remaining_time)
            try:
                await asyncio.wait_for(app.shutdown(), timeout=final_timeout)
                logger.info("Application shutdown complete")
            except asyncio.TimeoutError:
                logger.warning(f"Application shutdown timed out after {final_timeout}s")
            except Exception as e:
                logger.warning(f"Error during application shutdown: {e}")
                
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    # Give a brief moment for any remaining cleanup
    try:
        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass
    
    total_time = asyncio.get_event_loop().time() - start_time
    logger.info(f"Shutdown complete (took {total_time:.2f}s)")


async def main():
    """Main function to run the bot"""
    global app, scheduler, shutdown_event
    
    # Set up signal handlers for graceful shutdown early to avoid race conditions
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set up emergency exit handler for SIGALRM (if available on platform)
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, emergency_exit)
    
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
        # Set up emergency exit alarm as final safety net (45 seconds total)
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(45)  # Force exit after 45 seconds if shutdown hangs
        
        # Ensure shutdown doesn't hang indefinitely
        try:
            await asyncio.wait_for(shutdown(), timeout=35.0)  # Slightly longer than shutdown's internal timeout
        except asyncio.TimeoutError:
            logger.error("Shutdown process timed out after 35 seconds, forcing exit")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            # Cancel the emergency alarm if shutdown completed normally
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)


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
