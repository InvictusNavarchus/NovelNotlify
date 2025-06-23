#!/usr/bin/env python3
"""
Simple test to verify shutdown improvements work properly
"""

import asyncio
import sys
import signal
from novel_notify.main import shutdown_event, shutdown

async def test_shutdown_improvements():
    """Test that the shutdown mechanism works correctly"""
    print("🧪 Testing shutdown improvements...")
    
    # Test 1: Check shutdown event can be set
    try:
        shutdown_event.set()
        is_set = shutdown_event.is_set()
        print(f"✅ Shutdown event works: {is_set}")
        # Reset for next test
        shutdown_event.clear()
    except Exception as e:
        print(f"❌ Shutdown event test failed: {e}")
        return False
    
    # Test 2: Check shutdown function works without app/scheduler
    try:
        await shutdown()
        print("✅ Shutdown function works without active app")
    except Exception as e:
        print(f"❌ Shutdown function test failed: {e}")
        return False
    
    # Test 3: Check signal handler function exists and can be called
    try:
        from novel_notify.main import signal_handler
        # Don't actually call it with real signal as it would exit
        print("✅ Signal handler function is accessible")
    except Exception as e:
        print(f"❌ Signal handler test failed: {e}")
        return False
    
    print("✅ All shutdown improvement tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Testing shutdown improvements...")
    try:
        result = asyncio.run(test_shutdown_improvements())
        if result:
            print("✅ Shutdown improvements test completed successfully!")
            sys.exit(0)
        else:
            print("❌ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
