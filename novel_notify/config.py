"""
Configuration management for the Novel Notify bot
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        self.telegram_bot_token = self._get_required_env("TELEGRAM_BOT_TOKEN")
        self.check_interval = int(os.getenv("CHECK_INTERVAL", "3600"))  # Default: 1 hour
        self.database_path = os.getenv("DATABASE_PATH", "novels.db")
        self.cors_proxy_url = os.getenv("CORS_PROXY_URL", "https://cors.fadel.web.id/")
        
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    @property
    def webnovel_base_url(self) -> str:
        """Get WebNovel base URL with CORS proxy"""
        return f"{self.cors_proxy_url}https://www.webnovel.com"


# Global config instance
config = Config()
