"""
Info plugin for UserBot
Get information about users, chats, and messages
"""

from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, User, Chat
from pyrogram.enums import ChatType, UserStatus

from plugin_loader import message_handler

# Plugin info
__plugin_info__ = {
    'name': 'Info',
    'description': 'Get information about users, chats, and messages',
    'version': '1.0.0',
    'commands': ['info', 'id', 'chatinfo', 'msginfo']
}

# Global variables
client_ref = None
db_ref = None
config_ref = None

async def init_plugin(client, db, config):
    """Initialize the info plugin"""
    global client_ref, db_ref, config_ref
    client_ref = client
    db_ref = db
    config_ref = config

@message_handler(filters.command("info", ".") & filters.me)
async def info_command(client, message: Message):
    """Get user information"""
    try:
        # Get target user
        target_user = None
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            try:
                user_input = message.command[1]
                if user_input.startswith('@'):
                    target_user = await client.get_users(user_input)
                else:
                    target_user = await client.get_users(int(user_input))
            except:
                await message.edit("❌ **Error:** User not found")
                return
        else:
            target_user = message.from_user
        
        if not target_user:
            await message.edit("❌ **Error:** Could not identify user")
            return
        
        # Format user information
        info_text = f"👤 **User Information**\n\n"
        info_text += f"**Name:** {target_user.first_name}"
        
        if target_user.last_name:
            info_text += f" {target_user.last_name}"
        
        info_text += f"\n**Username:** @{target_user.username or 'None'}"
        info_text += f"\n**User ID:** `{target_user.id}`"
        info_text += f"\n**Language:** {target_user.language_code or 'Unknown'}"
        
        # Status information
        if target_user.status:
            status_map = {
                UserStatus.ONLINE: "🟢 Online",
                UserStatus.OFFLINE: "⚫ Offline", 
                UserStatus.RECENTLY: "🟡 Recently",
                UserStatus.LAST_WEEK: "🟠 Last Week",
                UserStatus.LAST_MONTH: "🔴 Last Month",
                UserStatus.LONG_AGO: "⚪ Long Ago"
            }
            info_text += f"\n**Status:** {status_map.get(target_user.status, 'Unknown')}"
        
        # Bot status
        if target_user.is_bot:
            info_text += f"\n**Type:** 🤖 Bot"
        elif target_user.is_verified:
            info_text += f"\n**Type:** ✅ Verified"
        elif target_user.is_premium:
            info_text += f"\n**Type:** ⭐ Premium"
        elif target_user.is_scam:
            info_text += f"\n**Type:** ⚠️ Scam"
        elif target_user.is_fake:
            info_text += f"\n**Type:** ❌ Fake"
        else:
            info_text += f"\n**Type:** 👤 Regular User"
        
        # Additional information
        if target_user.dc_id:
            info_text += f"\n**DC ID:** {target_user.dc_id}"
        
        # Common chats count
        try:
            common_chats = await client.get_common_chats(target_user.id)
            info_text += f"\n**Common Chats:** {len(common_chats)}"
        except:
            pass
        
        # User stats from database
        user_stats = await db_ref.get_user_stats(target_user.id)
        if user_stats:
            info_text += f"\n\n📊 **Statistics:**"
            info_text += f"\n**Messages:** {user_stats['total_messages']}"
            info_text += f"\n**Commands:** {user_stats['commands_used']}"
            if user_stats['last_seen']:
                info_text += f"\n**Last Seen:** {user_stats['last_seen']}"
        
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

@message_handler(filters.command("id", ".") & filters.me)
async def id_command(client, message: Message):
    """Get IDs of user/chat"""
    try:
        id_text = f"🆔 **ID Information**\n\n"
        
        # Chat information
        chat = message.chat
        id_text += f"**Chat ID:** `{chat.id}`\n"
        id_text += f"**Chat Type:** {chat.type.name.title()}\n"
        
        if chat.username:
            id_text += f"**Chat Username:** @{chat.username}\n"
        
        # User information
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            if user:
                id_text += f"\n**Replied User:**\n"
                id_text += f"├ **Name:** {user.first_name}"
                if user.last_name:
                    id_text += f" {user.last_name}"
                id_text += f"\n├ **Username:** @{user.username or 'None'}"
                id_text += f"\n└ **User ID:** `{user.id}`"
        else:
            user = message.from_user
            id_text += f"\n**Your Info:**\n"
            id_text += f"├ **Name:** {user.first_name}"
            if user.last_name:
                id_text += f" {user.last_name}"
            id_text += f"\n├ **Username:** @{user.username or 'None'}"
            id_text += f"\n└ **User ID:** `{user.id}`"
        
        # Message ID
        id_text += f"\n**Message ID:** `{message.id}`"
        
        await message.edit(id_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("chatinfo", ".") & filters.me)
async def chatinfo_command(client, message: Message):
    """Get chat information"""
    try:
        chat = message.chat
        
        info_text = f"💬 **Chat Information**\n\n"
        info_text += f"**Title:** {chat.title or 'Private Chat'}\n"
        info_text += f"**Chat ID:** `{chat.id}`\n"
        info_text += f"**Type:** {chat.type.name.title()}\n"
        
        if chat.username:
            info_text += f"**Username:** @{chat.username}\n"
        
        if chat.description:
            info_text += f"**Description:** {chat.description[:100]}{'...' if len(chat.description) > 100 else ''}\n"
        
        # Group/Channel specific info
        if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            try:
                full_chat = await client.get_chat(chat.id)
                info_text += f"**Members:** {full_chat.members_count or 'Unknown'}\n"
                
                if full_chat.linked_chat:
                    info_text += f"**Linked Chat:** {full_chat.linked_chat.title}\n"
                
                if hasattr(full_chat, 'slow_mode_delay') and full_chat.slow_mode_delay:
                    info_text += f"**Slow Mode:** {full_chat.slow_mode_delay}s\n"
                
            except:
                pass
        
        elif chat.type == ChatType.CHANNEL:
            try:
                full_chat = await client.get_chat(chat.id)
                info_text += f"**Subscribers:** {full_chat.members_count or 'Unknown'}\n"
                
                if full_chat.linked_chat:
                    info_text += f"**Discussion Group:** {full_chat.linked_chat.title}\n"
                    
            except:
                pass
        
        # Permissions and restrictions
        if chat.type != ChatType.PRIVATE:
            permissions = []
            
            try:
                full_chat = await client.get_chat(chat.id)
                if hasattr(full_chat, 'permissions'):
                    perms = full_chat.permissions
                    if perms.can_send_messages:
                        permissions.append("💬 Send Messages")
                    if perms.can_send_media_messages:
                        permissions.append("📷 Send Media")
                    if perms.can_add_web_page_previews:
                        permissions.append("🔗 Add Links")
                    if perms.can_send_polls:
                        permissions.append("📊 Send Polls")
                
                if permissions:
                    info_text += f"\n**Permissions:**\n"
                    for perm in permissions[:5]:  # Show first 5
                        info_text += f"├ {perm}\n"
                    if len(permissions) > 5:
                        info_text += f"└ +{len(permissions)-5} more...\n"
                        
            except:
                pass
        
        # Creation date if available
        if hasattr(chat, 'date') and chat.date:
            info_text += f"\n**Created:** {chat.date.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
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

@message_handler(filters.command("msginfo", ".") & filters.me)
async def msginfo_command(client, message: Message):
    """Get message information"""
    try:
        target_msg = message.reply_to_message or message
        
        info_text = f"💌 **Message Information**\n\n"
        info_text += f"**Message ID:** `{target_msg.id}`\n"
        info_text += f"**Date:** {target_msg.date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        
        # Sender info
        if target_msg.from_user:
            user = target_msg.from_user
            info_text += f"**From:** {user.first_name}"
            if user.last_name:
                info_text += f" {user.last_name}"
            if user.username:
                info_text += f" (@{user.username})"
            info_text += f"\n**User ID:** `{user.id}`\n"
        
        # Message type
        msg_types = []
        if target_msg.text:
            msg_types.append("📝 Text")
        if target_msg.photo:
            msg_types.append("📷 Photo")
        if target_msg.video:
            msg_types.append("🎥 Video")
        if target_msg.audio:
            msg_types.append("🎵 Audio")
        if target_msg.voice:
            msg_types.append("🎤 Voice")
        if target_msg.document:
            msg_types.append("📄 Document")
        if target_msg.sticker:
            msg_types.append("🎭 Sticker")
        if target_msg.animation:
            msg_types.append("🎬 GIF")
        if target_msg.poll:
            msg_types.append("📊 Poll")
        if target_msg.contact:
            msg_types.append("👤 Contact")
        if target_msg.location:
            msg_types.append("📍 Location")
        
        if msg_types:
            info_text += f"**Type:** {', '.join(msg_types)}\n"
        
        # Message stats
        if target_msg.views:
            info_text += f"**Views:** {target_msg.views:,}\n"
        
        if target_msg.forwards:
            info_text += f"**Forwards:** {target_msg.forwards:,}\n"
        
        # Edit info
        if target_msg.edit_date:
            info_text += f"**Edited:** {target_msg.edit_date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        
        # Reply info
        if target_msg.reply_to_message:
            reply_msg = target_msg.reply_to_message
            info_text += f"**Reply To:** Message `{reply_msg.id}`"
            if reply_msg.from_user:
                info_text += f" by {reply_msg.from_user.first_name}"
            info_text += "\n"
        
        # Forward info
        if target_msg.forward_date:
            info_text += f"**Forwarded:** {target_msg.forward_date.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            if target_msg.forward_from:
                info_text += f"**Original Sender:** {target_msg.forward_from.first_name}\n"
            elif target_msg.forward_from_chat:
                info_text += f"**Original Chat:** {target_msg.forward_from_chat.title}\n"
        
        # Text length
        if target_msg.text:
            info_text += f"**Text Length:** {len(target_msg.text)} characters\n"
        
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

async def cleanup_plugin():
    """Cleanup when plugin is unloaded"""
    pass
