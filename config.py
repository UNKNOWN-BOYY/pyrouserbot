"""
Configuration management for UserBot
Handles environment variables and default settings
"""

import os
from typing import Optional

class Config:
    """Configuration class for UserBot"""
    
    def __init__(self):
        # Required Telegram API credentials
        self.API_ID = int(os.getenv("API_ID", "0"))
        self.API_HASH = os.getenv("API_HASH", "")
        self.SESSION_STRING = os.getenv("SESSION_STRING", "")
        
        # Bot configuration
        self.BOT_PREFIX = os.getenv("BOT_PREFIX", ".")
        self.LOG_CHAT_ID = self._get_log_chat_id()
        
        # Database configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///userbot.db")
        
        # PM Permit settings
        self.PM_PERMIT_ENABLED = os.getenv("PM_PERMIT_ENABLED", "true").lower() == "true"
        self.PM_PERMIT_MESSAGE = os.getenv(
            "PM_PERMIT_MESSAGE",
            "🚫 **PM PERMIT ACTIVATED**\n\n"
            "You are not approved to PM me.\n"
            "Please wait for approval or contact me in a group."
        )
        self.PM_PERMIT_LIMIT = int(os.getenv("PM_PERMIT_LIMIT", "5"))
        
        # Alive plugin settings
        self.ALIVE_MESSAGE = os.getenv(
            "ALIVE_MESSAGE",
            "🤖 **UserBot is Alive!**\n\n"
            "📊 **System Status:** Online\n"
            "⏱️ **Uptime:** {uptime}\n"
            "🔧 **Version:** 1.0.0\n"
            "⚡ **Ping:** {ping}ms"
        )
        
        # Plugin settings
        self.DISABLED_PLUGINS = self._parse_list(os.getenv("DISABLED_PLUGINS", ""))
        
        # Validate configuration
        self._validate()
    
    def _get_log_chat_id(self) -> Optional[int]:
        """Get log chat ID from environment"""
        try:
            log_chat = os.getenv("LOG_CHAT_ID")
            if log_chat:
                return int(log_chat)
        except ValueError:
            pass
        return None
    
    def _parse_list(self, value: str) -> list:
        """Parse comma-separated string to list"""
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]
    
    def _validate(self):
        """Validate required configuration"""
        errors = []
        
        if not self.API_ID or self.API_ID == 0:
            errors.append("API_ID is required")
        
        if not self.API_HASH:
            errors.append("API_HASH is required")
        
        if not self.SESSION_STRING:
            errors.append("SESSION_STRING is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    def get_db_path(self) -> str:
        """Get database file path"""
        if self.DATABASE_URL.startswith("sqlite:///"):
            return self.DATABASE_URL[10:]  # Remove sqlite:/// prefix
        return "userbot.db"
    
    def is_plugin_disabled(self, plugin_name: str) -> bool:
        """Check if a plugin is disabled"""
        return plugin_name.lower() in [p.lower() for p in self.DISABLED_PLUGINS]
