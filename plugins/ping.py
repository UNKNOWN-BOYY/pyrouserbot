"""
Ping plugin for UserBot
Network latency and response time testing
"""

import asyncio
import time
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message

from plugin_loader import message_handler

# Plugin info
__plugin_info__ = {
    'name': 'Ping',
    'description': 'Network latency and response time testing',
    'version': '1.0.0',
    'commands': ['ping', 'pings', 'ping5']
}

# Global variables
client_ref = None
db_ref = None
config_ref = None

async def init_plugin(client, db, config):
    """Initialize the ping plugin"""
    global client_ref, db_ref, config_ref
    client_ref = client
    db_ref = db
    config_ref = config

@message_handler(filters.command("ping", ".") & filters.me)
async def ping_command(client, message: Message):
    """Simple ping command"""
    try:
        start_time = time.time()
        await message.edit("🏓 **Pinging...**")
        end_time = time.time()
        
        ping_ms = (end_time - start_time) * 1000
        
        # Determine quality
        if ping_ms < 50:
            quality = "🟢 Excellent"
        elif ping_ms < 100:
            quality = "🟡 Good"  
        elif ping_ms < 200:
            quality = "🟠 Average"
        else:
            quality = "🔴 Poor"
        
        ping_text = f"🏓 **Pong!**\n\n"
        ping_text += f"**Response Time:** `{ping_ms:.2f}ms`\n"
        ping_text += f"**Quality:** {quality}"
        
        await message.edit(ping_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("pings", ".") & filters.me)
async def ping_detailed_command(client, message: Message):
    """Detailed ping with multiple measurements"""
    try:
        await message.edit("🏓 **Running detailed ping test...**")
        
        ping_times = []
        
        # Perform 5 ping tests
        for i in range(5):
            start_time = time.time()
            temp_msg = await message.edit(f"🏓 **Ping test {i+1}/5...**")
            end_time = time.time()
            
            ping_ms = (end_time - start_time) * 1000
            ping_times.append(ping_ms)
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        # Calculate statistics
        avg_ping = sum(ping_times) / len(ping_times)
        min_ping = min(ping_times)
        max_ping = max(ping_times)
        
        # Determine overall quality
        if avg_ping < 50:
            quality = "🟢 Excellent"
        elif avg_ping < 100:
            quality = "🟡 Good"
        elif avg_ping < 200:
            quality = "🟠 Average"
        else:
            quality = "🔴 Poor"
        
        # Format results
        ping_text = f"🏓 **Detailed Ping Results**\n\n"
        ping_text += f"**Average:** `{avg_ping:.2f}ms`\n"
        ping_text += f"**Minimum:** `{min_ping:.2f}ms`\n"
        ping_text += f"**Maximum:** `{max_ping:.2f}ms`\n"
        ping_text += f"**Quality:** {quality}\n\n"
        
        ping_text += f"**Individual Results:**\n"
        for i, ping_time in enumerate(ping_times, 1):
            ping_text += f"└ Test {i}: `{ping_time:.2f}ms`\n"
        
        await message.edit(ping_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("ping5", ".") & filters.me)
async def ping_five_command(client, message: Message):
    """Quick 5-ping test"""
    try:
        start_msg = await message.edit("🏓 **Quick ping test...**")
        
        ping_times = []
        
        # Perform 5 quick tests
        for i in range(5):
            start_time = time.time()
            await start_msg.edit(f"🏓 **Ping {i+1}/5:** Testing...")
            end_time = time.time()
            
            ping_ms = (end_time - start_time) * 1000
            ping_times.append(ping_ms)
        
        # Calculate average
        avg_ping = sum(ping_times) / len(ping_times)
        
        # Determine quality
        if avg_ping < 50:
            quality = "🟢 Excellent"
            emoji = "🚀"
        elif avg_ping < 100:
            quality = "🟡 Good"
            emoji = "⚡"
        elif avg_ping < 200:
            quality = "🟠 Average"
            emoji = "🐌"
        else:
            quality = "🔴 Poor"
            emoji = "🦴"
        
        ping_text = f"{emoji} **Ping Results**\n\n"
        ping_text += f"**Average:** `{avg_ping:.2f}ms`\n"
        ping_text += f"**Quality:** {quality}\n"
        ping_text += f"**Tests:** {len(ping_times)} samples"
        
        await start_msg.edit(ping_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("dc", ".") & filters.me)
async def datacenter_command(client, message: Message):
    """Show datacenter information"""
    try:
        # Get session info
        me = await client.get_me()
        
        dc_text = f"🌐 **Datacenter Information**\n\n"
        dc_text += f"**User ID:** `{me.id}`\n"
        dc_text += f"**Username:** @{me.username or 'None'}\n"
        dc_text += f"**Name:** {me.first_name}"
        
        if me.last_name:
            dc_text += f" {me.last_name}"
        
        # Try to get DC info if available
        try:
            session = client.session
            if hasattr(session, 'dc_id'):
                dc_text += f"\n**DC ID:** {session.dc_id}"
        except:
            pass
        
        await message.edit(dc_text)
        
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
