#!/usr/bin/env python3
"""
Setup script for Novel Notify Bot
"""

import os
import sys

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = ".env"
    
    if os.path.exists(env_path):
        print("✅ .env file already exists")
        return
    
    print("🔧 Creating .env file...")
    
    # Get bot token from user
    bot_token = input("Enter your Telegram Bot Token: ").strip()
    
    if not bot_token:
        print("❌ Bot token is required!")
        return False
    
    # Default settings
    check_interval = input("Enter check interval in seconds [3600]: ").strip() or "3600"
    database_path = input("Enter database path [novels.db]: ").strip() or "novels.db"
    cors_proxy = input("Enter CORS proxy URL [https://cors.fadel.web.id/]: ").strip() or "https://cors.fadel.web.id/"
    
    # Create .env file
    env_content = f"""TELEGRAM_BOT_TOKEN={bot_token}
CHECK_INTERVAL={check_interval}
DATABASE_PATH={database_path}
CORS_PROXY_URL={cors_proxy}
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    return True

def main():
    """Main setup function"""
    print("📚 Novel Notify Bot Setup")
    print("=" * 30)
    
    # Create .env file
    if not create_env_file():
        return
    
    print("\n🚀 Setup complete!")
    print("\nNext steps:")
    print("1. Make sure your bot token is correct")
    print("2. Run the bot with: uv run python -m novel_notify.main")
    print("3. Or use the convenience script: uv run python run.py")
    print("\n📖 Check README.md for more information")

if __name__ == "__main__":
    main()
