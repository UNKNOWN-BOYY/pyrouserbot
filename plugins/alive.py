"""
Alive plugin for UserBot
Shows bot status and uptime information
"""

import psutil
import platform
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import Message

from plugin_loader import message_handler
from utils.helpers import format_uptime, get_system_info

# Plugin info
__plugin_info__ = {
    'name': 'Alive',
    'description': 'Show userbot status and uptime',
    'version': '1.0.0',
    'commands': ['alive', 'ping', 'uptime', 'stats']
}

# Global variables
start_time = datetime.now()
client_ref = None
db_ref = None
config_ref = None

async def init_plugin(client, db, config):
    """Initialize the alive plugin"""
    global client_ref, db_ref, config_ref, start_time
    client_ref = client
    db_ref = db
    config_ref = config
    start_time = datetime.now()

@message_handler(filters.command(["alive", "up"], ".") & filters.me)
async def alive_command(client, message: Message):
    """Handle alive command"""
    try:
        # Calculate uptime
        uptime = datetime.now() - start_time
        uptime_str = format_uptime(uptime)
        
        # Get system info
        system_info = get_system_info()
        
        # Calculate ping
        ping_start = datetime.now()
        temp_msg = await message.reply("Calculating ping...")
        ping_end = datetime.now()
        ping_ms = (ping_end - ping_start).total_seconds() * 1000
        await temp_msg.delete()
        
        # Format alive message
        alive_text = config_ref.ALIVE_MESSAGE.format(
            uptime=uptime_str,
            ping=f"{ping_ms:.1f}"
        )
        
        # Add system information
        alive_text += f"\n\n📱 **System Info:**\n"
        alive_text += f"**OS:** {system_info['os']}\n"
        alive_text += f"**CPU:** {system_info['cpu_percent']}%\n"
        alive_text += f"**RAM:** {system_info['memory_percent']}%\n"
        alive_text += f"**Disk:** {system_info['disk_percent']}%\n"
        alive_text += f"**Python:** {system_info['python_version']}"
        
        # Send alive message
        await message.edit(alive_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("uptime", ".") & filters.me)
async def uptime_command(client, message: Message):
    """Handle uptime command"""
    try:
        uptime = datetime.now() - start_time
        uptime_str = format_uptime(uptime)
        
        uptime_text = f"⏱️ **Uptime Information**\n\n"
        uptime_text += f"**Bot Uptime:** {uptime_str}\n"
        uptime_text += f"**Started:** {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        
        # System uptime
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            system_uptime = datetime.now() - boot_time
            uptime_text += f"**System Uptime:** {format_uptime(system_uptime)}"
        except:
            pass
        
        await message.edit(uptime_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("ping", ".") & filters.me)
async def ping_command(client, message: Message):
    """Handle ping command"""
    try:
        # Measure ping
        ping_start = datetime.now()
        temp_msg = await message.edit("🏓 **Pinging...**")
        ping_end = datetime.now()
        
        ping_ms = (ping_end - ping_start).total_seconds() * 1000
        
        # Determine ping quality
        if ping_ms < 100:
            quality = "🟢 Excellent"
        elif ping_ms < 200:
            quality = "🟡 Good"
        elif ping_ms < 500:
            quality = "🟠 Average"
        else:
            quality = "🔴 Poor"
        
        ping_text = f"🏓 **Pong!**\n\n"
        ping_text += f"**Ping:** {ping_ms:.1f}ms\n"
        ping_text += f"**Quality:** {quality}\n"
        ping_text += f"**Time:** {ping_end.strftime('%H:%M:%S')}"
        
        await temp_msg.edit(ping_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("sysstats", ".") & filters.me)
async def system_stats_command(client, message: Message):
    """Handle system stats command"""
    try:
        system_info = get_system_info()
        
        stats_text = f"💻 **System Statistics**\n\n"
        stats_text += f"**Operating System:**\n"
        stats_text += f"├ OS: {system_info['os']}\n"
        stats_text += f"├ Architecture: {platform.architecture()[0]}\n"
        stats_text += f"└ Processor: {platform.processor() or 'Unknown'}\n\n"
        
        stats_text += f"**Resource Usage:**\n"
        stats_text += f"├ CPU Usage: {system_info['cpu_percent']}%\n"
        stats_text += f"├ Memory Usage: {system_info['memory_percent']}%\n"
        stats_text += f"├ Disk Usage: {system_info['disk_percent']}%\n"
        stats_text += f"└ Available Memory: {system_info['memory_available']}\n\n"
        
        stats_text += f"**Runtime Info:**\n"
        stats_text += f"├ Python Version: {system_info['python_version']}\n"
        stats_text += f"└ Bot Uptime: {format_uptime(datetime.now() - start_time)}"
        
        await message.edit(stats_text)
        
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
