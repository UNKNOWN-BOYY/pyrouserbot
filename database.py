"""
Database management for UserBot
Handles SQLite operations and data persistence
"""

import aiosqlite
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """Database handler for UserBot"""
    
    def __init__(self, db_path: str = "userbot.db"):
        self.db_path = db_path
        self.connection = None
    
    async def initialize(self):
        """Initialize database and create tables"""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self):
        """Create necessary database tables"""
        tables = [
            # PM Permit table
            """
            CREATE TABLE IF NOT EXISTS pm_permits (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                approved BOOLEAN DEFAULT FALSE,
                approved_by INTEGER,
                approved_at TIMESTAMP,
                warnings INTEGER DEFAULT 0,
                last_warning TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # User statistics table
            """
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                total_messages INTEGER DEFAULT 0,
                commands_used INTEGER DEFAULT 0,
                last_seen TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Plugin settings table
            """
            CREATE TABLE IF NOT EXISTS plugin_settings (
                plugin_name TEXT,
                setting_key TEXT,
                setting_value TEXT,
                user_id INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (plugin_name, setting_key, user_id)
            )
            """,
            
            # Bot logs table
            """
            CREATE TABLE IF NOT EXISTS bot_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                user_id INTEGER,
                chat_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            await self.connection.execute(table_sql)
        
        await self.connection.commit()
        logger.info("Database tables created/verified")
    
    # PM Permit methods
    async def get_pm_permit(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get PM permit status for a user"""
        async with self.connection.execute(
            "SELECT * FROM pm_permits WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
        return None
    
    async def add_pm_permit(self, user_id: int, username: str = None, 
                           first_name: str = None, approved: bool = False,
                           approved_by: int = None) -> bool:
        """Add or update PM permit entry"""
        try:
            now = datetime.now()
            await self.connection.execute(
                """
                INSERT OR REPLACE INTO pm_permits 
                (user_id, username, first_name, approved, approved_by, approved_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, username, first_name, approved, 
                 approved_by, now if approved else None, now)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add PM permit: {e}")
            return False
    
    async def approve_pm(self, user_id: int, approved_by: int) -> bool:
        """Approve a user for PM"""
        try:
            now = datetime.now()
            await self.connection.execute(
                """
                UPDATE pm_permits 
                SET approved = TRUE, approved_by = ?, approved_at = ?
                WHERE user_id = ?
                """,
                (approved_by, now, user_id)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to approve PM: {e}")
            return False
    
    async def disapprove_pm(self, user_id: int) -> bool:
        """Disapprove a user for PM"""
        try:
            await self.connection.execute(
                """
                UPDATE pm_permits 
                SET approved = FALSE, approved_by = NULL, approved_at = NULL
                WHERE user_id = ?
                """,
                (user_id,)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to disapprove PM: {e}")
            return False
    
    async def add_pm_warning(self, user_id: int) -> int:
        """Add warning to PM permit and return total warnings"""
        try:
            now = datetime.now()
            # Get current warnings
            permit = await self.get_pm_permit(user_id)
            warnings = (permit['warnings'] if permit else 0) + 1
            
            if permit:
                await self.connection.execute(
                    """
                    UPDATE pm_permits 
                    SET warnings = ?, last_warning = ?
                    WHERE user_id = ?
                    """,
                    (warnings, now, user_id)
                )
            else:
                await self.connection.execute(
                    """
                    INSERT INTO pm_permits 
                    (user_id, warnings, last_warning, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, warnings, now, now)
                )
            
            await self.connection.commit()
            return warnings
        except Exception as e:
            logger.error(f"Failed to add PM warning: {e}")
            return 0
    
    # User statistics methods
    async def update_user_stats(self, user_id: int, username: str = None,
                               first_name: str = None, message_count: int = 0,
                               command_count: int = 0) -> bool:
        """Update user statistics"""
        try:
            now = datetime.now()
            await self.connection.execute(
                """
                INSERT OR REPLACE INTO user_stats 
                (user_id, username, first_name, total_messages, commands_used, last_seen, updated_at)
                VALUES (
                    ?, ?, ?, 
                    COALESCE((SELECT total_messages FROM user_stats WHERE user_id = ?), 0) + ?,
                    COALESCE((SELECT commands_used FROM user_stats WHERE user_id = ?), 0) + ?,
                    ?, ?
                )
                """,
                (user_id, username, first_name, user_id, message_count, 
                 user_id, command_count, now, now)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update user stats: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        async with self.connection.execute(
            "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
        return None
    
    # Plugin settings methods
    async def get_plugin_setting(self, plugin_name: str, setting_key: str, 
                                user_id: int = 0) -> Optional[str]:
        """Get plugin setting value"""
        async with self.connection.execute(
            """
            SELECT setting_value FROM plugin_settings 
            WHERE plugin_name = ? AND setting_key = ? AND user_id = ?
            """,
            (plugin_name, setting_key, user_id)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
    
    async def set_plugin_setting(self, plugin_name: str, setting_key: str,
                                setting_value: str, user_id: int = 0) -> bool:
        """Set plugin setting value"""
        try:
            now = datetime.now()
            await self.connection.execute(
                """
                INSERT OR REPLACE INTO plugin_settings 
                (plugin_name, setting_key, setting_value, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (plugin_name, setting_key, setting_value, user_id, now)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to set plugin setting: {e}")
            return False
    
    # Logging methods
    async def add_log(self, level: str, message: str, user_id: int = None,
                     chat_id: int = None) -> bool:
        """Add log entry to database"""
        try:
            await self.connection.execute(
                """
                INSERT INTO bot_logs (level, message, user_id, chat_id)
                VALUES (?, ?, ?, ?)
                """,
                (level, message, user_id, chat_id)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add log: {e}")
            return False
    
    # General methods
    async def execute_query(self, query: str, parameters: tuple = ()) -> bool:
        """Execute a custom query"""
        try:
            await self.connection.execute(query, parameters)
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return False
    
    async def fetch_query(self, query: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch results from a custom query"""
        try:
            async with self.connection.execute(query, parameters) as cursor:
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch query: {e}")
            return []
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
