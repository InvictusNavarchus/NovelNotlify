#!/usr/bin/env python3
"""
Test script to verify graceful shutdown behavior
"""

import asyncio
import signal
import sys
import time
from novel_notify.main import main, shutdown_event, shutdown

async def test_shutdown():
    """Test the shutdown mechanism"""
    print("Testing shutdown mechanism...")
    
    # Create a task that will run main()
    main_task = asyncio.create_task(main())
    
    # Wait a bit to let the bot initialize
    await asyncio.sleep(2)
    
    print("Setting shutdown event...")
    shutdown_event.set()
    
    # Wait for main to finish
    try:
        await asyncio.wait_for(main_task, timeout=10)
        print("✅ Main task completed gracefully")
    except asyncio.TimeoutError:
        print("❌ Main task did not complete within timeout")
        main_task.cancel()
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")

if __name__ == "__main__":
    # Only run this test if we have a valid bot token
    from novel_notify.config import config
    
    if not config.telegram_bot_token or config.telegram_bot_token == "your_bot_token_here":
        print("⚠️  No valid bot token found. This test requires a real bot token.")
        print("Set up your .env file with a valid TELEGRAM_BOT_TOKEN to run this test.")
        sys.exit(0)
    
    print("🚀 Testing graceful shutdown...")
    try:
        asyncio.run(test_shutdown())
        print("✅ Shutdown test completed successfully!")
    except KeyboardInterrupt:
        print("❌ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")
