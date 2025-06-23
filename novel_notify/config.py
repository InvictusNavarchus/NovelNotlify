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


# Global config instance, loaded on first access
_config_instance = None

def load_app_config() -> Config:
    """Loads and returns the application configuration."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

# Make it accessible as 'config' for existing import patterns,
# but it's now a function that needs to be called.
# For direct use: from novel_notify.config import load_app_config; cfg = load_app_config()
# For patching: mock the load_app_config function or the _config_instance.
# To maintain the 'config.VARIABLE' access pattern after first load,
# we can assign the loaded config to a module level variable if preferred,
# but using a function is cleaner for testing. Let's try this first.

# If we want to keep the direct 'config.VARIABLE' style after initial import in app code (not tests):
# config = load_app_config()
# However, this would re-trigger the original problem for tests.
# So, application code will need to change from 'from .config import config' to
# 'from .config import load_app_config' and then 'app_config = load_app_config()'.

# For minimal changes to app code, let's try a lazy loader property approach for 'config'
class ConfigProxy:
    _instance = None
    def __getattr__(self, name):
        if ConfigProxy._instance is None:
            ConfigProxy._instance = Config()
        return getattr(ConfigProxy._instance, name)

config = ConfigProxy()
