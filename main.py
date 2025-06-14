#!/usr/bin/env python3
"""
Telegram Userbot - Main Application
Built with Pyrogram for Koyeb deployment
"""

import asyncio
import logging
import os
import signal
import sys
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AuthKeyUnregistered

from config import Config
from database import Database
from plugin_loader import PluginLoader
from utils.helpers import format_uptime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('userbot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class UserBot:
    """Main UserBot class"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.config = Config()
        self.db = Database()
        self.client = None
        self.plugin_loader = None
        self.running = False
        
    async def initialize(self):
        """Initialize the userbot"""
        try:
            # Initialize database
            await self.db.initialize()
            logger.info("Database initialized successfully")
            
            # Create Pyrogram client
            self.client = Client(
                name="userbot",
                api_id=self.config.API_ID,
                api_hash=self.config.API_HASH,
                session_string=self.config.SESSION_STRING,
                in_memory=False
            )
            
            # Initialize plugin loader
            self.plugin_loader = PluginLoader(self.client, self.db, self.config)
            
            logger.info("UserBot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize UserBot: {e}")
            return False
    
    async def start(self):
        """Start the userbot"""
        try:
            # Start the client
            await self.client.start()
            
            # Get bot info
            me = await self.client.get_me()
            logger.info(f"UserBot started as {me.first_name} ({me.username or me.id})")
            
            # Load plugins
            await self.plugin_loader.load_all_plugins()
            
            # Set running flag
            self.running = True
            
            # Send startup message if configured
            if self.config.LOG_CHAT_ID:
                try:
                    await self.client.send_message(
                        self.config.LOG_CHAT_ID,
                        f"🤖 **UserBot Started**\n\n"
                        f"**User:** {me.first_name}\n"
                        f"**Username:** @{me.username or 'None'}\n"
                        f"**ID:** `{me.id}`\n"
                        f"**Plugins Loaded:** {len(self.plugin_loader.loaded_plugins)}\n"
                        f"**Start Time:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to send startup message: {e}")
            
            logger.info("UserBot is running...")
            
        except (ApiIdInvalid, ApiIdPublishedFlood, AuthKeyUnregistered) as e:
            logger.error(f"Telegram API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to start UserBot: {e}")
            raise
    
    async def stop(self):
        """Stop the userbot"""
        try:
            logger.info("Stopping UserBot...")
            self.running = False
            
            # Unload plugins
            if self.plugin_loader:
                await self.plugin_loader.unload_all_plugins()
            
            # Stop client
            if self.client:
                await self.client.stop()
            
            # Close database
            if self.db:
                await self.db.close()
            
            logger.info("UserBot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping UserBot: {e}")
    
    async def run(self):
        """Main run loop"""
        try:
            # Initialize
            if not await self.initialize():
                return False
            
            # Start
            await self.start()
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in run loop: {e}")
        finally:
            await self.stop()
        
        return True

# Global userbot instance
userbot = UserBot()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    userbot.running = False

async def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run the userbot
        success = await userbot.run()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required!")
        sys.exit(1)
    
    # Run the main function
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to run application: {e}")
        sys.exit(1)
