# Novel Notify Bot - Quick Command Reference

## Setup Commands
```bash
# Setup bot configuration
uv run python setup.py

# Test scraping functionality
uv run python test_scraping.py

# Start the bot
uv run python start_bot.py
```

## Bot Commands (in Telegram)
- `/start` - Welcome message and introduction
- `/help` - Show available commands
- `/add <url>` - Add a novel to track
- `/list` - Show all tracked novels
- `/remove <number>` - Remove novel by list number
- `/check` - Check for updates on all novels

## Usage Examples
```
# Add a novel
/add https://www.webnovel.com/book/32382246008650205

# Or just send the URL directly
https://www.webnovel.com/book/32382246008650205

# Remove a novel (use number from /list)
/remove 1
```

## Troubleshooting
```bash
# Check if dependencies are installed
uv run python -c "import telegram, httpx, bs4; print('All dependencies OK')"

# Test configuration
uv run python -c "from novel_notify.config import config; print('Config OK')"

# Test database
uv run python -c "from novel_notify.database import DatabaseManager; db = DatabaseManager(); print('Database OK')"
```
