# Novel Notify Bot

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)

A robust Telegram bot that monitors WebNovel pages for new chapter updates and notifies users when new chapters are available.

## Features

- 📚 Track multiple novels by URL
- 🔔 Automatic notifications for new chapters
- ⏰ Configurable check intervals
- 📊 View all tracked novels and their latest updates
- 🆕 Check for updates on demand
- 💾 Persistent storage with SQLite

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Run the setup script to configure the bot:
   ```bash
   uv run python setup.py
   ```
   This will create a `.env` file with your bot token and settings.

4. Test the scraping functionality (optional):
   ```bash
   uv run python test_scraping.py
   ```

5. Run the bot:
   ```bash
   uv run python start_bot.py
   ```

### Alternative Setup

You can also manually create a `.env` file with your bot token:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
CHECK_INTERVAL=3600  # Optional: Check interval in seconds (default: 1 hour)
DATABASE_PATH=novels.db  # Optional: Database file path
CORS_PROXY_URL=https://cors.fadel.web.id/  # CORS proxy for WebNovel requests
```

## Usage

### Quick Start

1. Start the bot: `uv run python start_bot.py`
2. Open Telegram and find your bot
3. Send `/start` to begin
4. Send a WebNovel URL to start tracking a novel

### Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show available commands
- `/add <url>` - Add a novel to track (WebNovel URL)
- `/list` - Show all tracked novels
- `/remove <novel_id>` - Remove a novel from tracking
- `/check` - Check for updates on all tracked novels

### Adding Novels

Simply send a WebNovel URL to the bot or use the `/add` command:
```
/add https://www.webnovel.com/book/32382246008650205
```

The bot supports both URL formats:
- With title: `https://www.webnovel.com/book/title_id`
- ID only: `https://www.webnovel.com/book/id`

### Adding Novels

Simply send a WebNovel URL to the bot or use the `/add` command:
```
/add https://www.webnovel.com/book/32382246008650205
```

The bot supports both URL formats:
- With title: `https://www.webnovel.com/book/title_id`
- ID only: `https://www.webnovel.com/book/id`

## Development

### Project Structure

```
novel_notify/
├── __init__.py
├── main.py              # Bot entry point
├── bot/
│   ├── __init__.py
│   ├── handlers.py      # Command and message handlers
│   └── scheduler.py     # Background task scheduler
├── scraper/
│   ├── __init__.py
│   ├── webnovel.py      # WebNovel scraping logic
│   └── models.py        # Data models
├── database/
│   ├── __init__.py
│   ├── manager.py       # Database operations
│   └── models.py        # Database schema
└── utils/
    ├── __init__.py
    ├── config.py        # Configuration management
    └── helpers.py       # Utility functions
```

## License

This project is licensed under GPL-3.0. See [LICENSE](LICENSE) for details.
