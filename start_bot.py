#!/usr/bin/env python3
"""
Simple start script for Novel Notify Bot
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Main entry point"""
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Run 'uv run python setup.py' first to configure the bot.")
        sys.exit(1)
    
    # Import and run the bot
    from novel_notify.main import run
    run()

if __name__ == "__main__":
    main()
