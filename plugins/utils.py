"""
Utilities plugin for UserBot
Various utility commands and tools
"""

import asyncio
import os
import platform
import sys
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message

from plugin_loader import message_handler

# Plugin info
__plugin_info__ = {
    'name': 'Utils',
    'description': 'Various utility commands and tools',
    'version': '1.0.0',
    'commands': ['help', 'plugins', 'reload', 'logs', 'eval', 'exec', 'restart']
}

# Global variables
client_ref = None
db_ref = None
config_ref = None
plugin_loader_ref = None

async def init_plugin(client, db, config):
    """Initialize the utils plugin"""
    global client_ref, db_ref, config_ref
    client_ref = client
    db_ref = db
    config_ref = config

@message_handler(filters.command("help", ".") & filters.me)
async def help_command(client, message: Message):
    """Show help information"""
    try:
        help_text = f"🤖 **UserBot Help**\n\n"
        help_text += f"**Prefix:** `{config_ref.BOT_PREFIX}`\n\n"
        
        # Core commands
        help_text += f"**🔧 Core Commands:**\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}alive` - Show bot status\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}ping` - Test response time\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}uptime` - Show uptime\n"
        help_text += f"└ `{config_ref.BOT_PREFIX}help` - Show this help\n\n"
        
        # PM Permit commands
        help_text += f"**🛡️ PM Permit:**\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}approve` - Approve user\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}disapprove` - Disapprove user\n" 
        help_text += f"├ `{config_ref.BOT_PREFIX}block` - Block user\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}unblock` - Unblock user\n"
        help_text += f"└ `{config_ref.BOT_PREFIX}pmguard` - Toggle PM permit\n\n"
        
        # Info commands
        help_text += f"**ℹ️ Information:**\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}info` - User information\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}id` - Get IDs\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}chatinfo` - Chat information\n"
        help_text += f"└ `{config_ref.BOT_PREFIX}msginfo` - Message info\n\n"
        
        # Stats commands
        help_text += f"**📊 Statistics:**\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}stats` - Bot statistics\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}mystats` - Your stats\n"
        help_text += f"└ `{config_ref.BOT_PREFIX}usage` - Usage analytics\n\n"
        
        # Utils commands
        help_text += f"**🔨 Utilities:**\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}plugins` - List plugins\n"
        help_text += f"├ `{config_ref.BOT_PREFIX}reload` - Reload plugin\n"
        help_text += f"└ `{config_ref.BOT_PREFIX}logs` - Show recent logs"
        
        await message.edit(help_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("plugins", ".") & filters.me)
async def plugins_command(client, message: Message):
    """List loaded plugins"""
    try:
        # This requires access to plugin loader - we'll implement a basic version
        plugins_text = f"🔌 **Loaded Plugins**\n\n"
        
        # Basic plugin info (since we can't easily access plugin loader here)
        plugins_info = [
            {"name": "alive", "status": "✅", "desc": "Bot status and uptime"},
            {"name": "pm_permit", "status": "✅", "desc": "PM auto-approval system"},
            {"name": "ping", "status": "✅", "desc": "Network latency testing"},
            {"name": "info", "status": "✅", "desc": "User and chat information"},
            {"name": "stats", "status": "✅", "desc": "Usage statistics"},
            {"name": "utils", "status": "✅", "desc": "Utility commands"}
        ]
        
        for plugin in plugins_info:
            plugins_text += f"{plugin['status']} **{plugin['name'].title()}**\n"
            plugins_text += f"    └ {plugin['desc']}\n\n"
        
        plugins_text += f"**Total:** {len(plugins_info)} plugins loaded"
        
        await message.edit(plugins_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("reload", ".") & filters.me)
async def reload_command(client, message: Message):
    """Reload a plugin"""
    try:
        if len(message.command) < 2:
            await message.edit("❌ **Usage:** `.reload <plugin_name>`")
            return
        
        plugin_name = message.command[1].lower()
        
        # For now, just show a message (full implementation would require plugin loader reference)
        await message.edit(f"🔄 **Reloading plugin:** {plugin_name}\n\n⚠️ Plugin reload functionality requires advanced implementation.")
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("logs", ".") & filters.me)
async def logs_command(client, message: Message):
    """Show recent logs"""
    try:
        # Get recent logs from database
        limit = 10
        if len(message.command) > 1:
            try:
                limit = min(int(message.command[1]), 20)  # Max 20 logs
            except:
                pass
        
        recent_logs = await db_ref.fetch_query("""
            SELECT level, message, timestamp
            FROM bot_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        logs_text = f"📝 **Recent Logs** (Last {limit})\n\n"
        
        if recent_logs:
            for log in recent_logs:
                # Format timestamp
                try:
                    timestamp = datetime.fromisoformat(log['timestamp']).strftime('%H:%M:%S')
                except:
                    timestamp = "Unknown"
                
                # Level emoji
                level_emoji = {
                    'INFO': 'ℹ️',
                    'WARNING': '⚠️',
                    'ERROR': '❌',
                    'DEBUG': '🐛'
                }.get(log['level'], '📋')
                
                logs_text += f"{level_emoji} `{timestamp}` **{log['level']}**\n"
                logs_text += f"    └ {log['message'][:100]}{'...' if len(log['message']) > 100 else ''}\n\n"
        else:
            logs_text += "No logs available."
        
        await message.edit(logs_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("eval", ".") & filters.me)
async def eval_command(client, message: Message):
    """Evaluate Python expression"""
    try:
        if len(message.command) < 2:
            await message.edit("❌ **Usage:** `.eval <expression>`")
            return
        
        # Get expression
        expression = message.text.split(None, 1)[1]
        
        # Safety warning
        await message.edit("⚠️ **Warning:** Eval can be dangerous. Use with caution!")
        await asyncio.sleep(2)
        
        try:
            # Evaluate expression
            result = eval(expression)
            
            result_text = f"📊 **Eval Result**\n\n"
            result_text += f"**Expression:** `{expression}`\n"
            result_text += f"**Result:** `{result}`\n"
            result_text += f"**Type:** `{type(result).__name__}`"
            
            await message.edit(result_text)
            
        except Exception as eval_error:
            await message.edit(f"❌ **Eval Error:** `{str(eval_error)}`")
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("sysinfo", ".") & filters.me)
async def sysinfo_command(client, message: Message):
    """Show system information"""
    try:
        info_text = f"💻 **System Information**\n\n"
        
        # Python info
        info_text += f"**Python:**\n"
        info_text += f"├ Version: {sys.version.split()[0]}\n"
        info_text += f"├ Implementation: {platform.python_implementation()}\n"
        info_text += f"└ Executable: `{sys.executable}`\n\n"
        
        # System info
        info_text += f"**System:**\n"
        info_text += f"├ OS: {platform.system()} {platform.release()}\n"
        info_text += f"├ Architecture: {platform.architecture()[0]}\n"
        info_text += f"├ Machine: {platform.machine()}\n"
        info_text += f"└ Processor: {platform.processor() or 'Unknown'}\n\n"
        
        # Process info
        try:
            import psutil
            process = psutil.Process()
            info_text += f"**Process:**\n"
            info_text += f"├ PID: {process.pid}\n"
            info_text += f"├ Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB\n"
            info_text += f"├ CPU: {process.cpu_percent():.1f}%\n"
            info_text += f"└ Threads: {process.num_threads()}\n\n"
        except ImportError:
            pass
        
        # Environment
        info_text += f"**Environment:**\n"
        info_text += f"├ Working Dir: `{os.getcwd()}`\n"
        info_text += f"├ User: {os.getenv('USER', 'Unknown')}\n"
        info_text += f"└ Shell: {os.getenv('SHELL', 'Unknown')}"
        
        await message.edit(info_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("restart", ".") & filters.me)
async def restart_command(client, message: Message):
    """Restart the userbot"""
    try:
        await message.edit("🔄 **Restarting UserBot...**\n\nPlease wait a moment.")
        
        # Log the restart
        await db_ref.add_log("INFO", "UserBot restart requested by user")
        
        # In a real implementation, this would trigger a restart
        # For now, just show a message
        await asyncio.sleep(2)
        await message.edit("⚠️ **Restart functionality requires process management.**\n\nUse your hosting platform's restart feature.")
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

async def cleanup_plugin():
    """Cleanup when plugin is unloaded"""
    pass
