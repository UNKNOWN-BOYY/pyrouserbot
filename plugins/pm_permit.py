"""
PM Permit plugin for UserBot
Auto-approval system for private messages with spam protection
"""

import asyncio
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import UserIsBlocked, PeerIdInvalid

from plugin_loader import message_handler

# Plugin info
__plugin_info__ = {
    'name': 'PM Permit',
    'description': 'Private message auto-approval system',
    'version': '1.0.0',
    'commands': ['approve', 'disapprove', 'block', 'unblock', 'pmguard']
}

# Global variables
client_ref = None
db_ref = None
config_ref = None
warned_users = {}  # Cache for warning counts

async def init_plugin(client, db, config):
    """Initialize the PM permit plugin"""
    global client_ref, db_ref, config_ref
    client_ref = client
    db_ref = db
    config_ref = config

@message_handler(filters.private & ~filters.me & ~filters.service)
async def handle_private_message(client, message: Message):
    """Handle incoming private messages"""
    if not config_ref.PM_PERMIT_ENABLED:
        return
    
    user_id = message.from_user.id
    
    # Skip if user is already approved
    permit = await db_ref.get_pm_permit(user_id)
    if permit and permit['approved']:
        # Update stats
        await db_ref.update_user_stats(
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            message_count=1
        )
        return
    
    # Check if user needs to be warned
    await handle_unapproved_user(message)

async def handle_unapproved_user(message: Message):
    """Handle message from unapproved user"""
    user_id = message.from_user.id
    user = message.from_user
    
    try:
        # Add warning to database
        warnings = await db_ref.add_pm_warning(user_id)
        
        # Update user info in database
        await db_ref.add_pm_permit(
            user_id,
            user.username,
            user.first_name,
            approved=False
        )
        
        # Send warning message if under limit
        if warnings <= config_ref.PM_PERMIT_LIMIT:
            warning_text = config_ref.PM_PERMIT_MESSAGE
            warning_text += f"\n\n⚠️ **Warning {warnings}/{config_ref.PM_PERMIT_LIMIT}**"
            
            if warnings == config_ref.PM_PERMIT_LIMIT:
                warning_text += "\n🚫 **Next message will result in a block!**"
            
            try:
                await client_ref.send_message(user_id, warning_text)
            except (UserIsBlocked, PeerIdInvalid):
                pass
        
        # Block user if exceeded limit
        elif warnings > config_ref.PM_PERMIT_LIMIT:
            try:
                await client_ref.block_user(user_id)
                
                # Log the block
                await db_ref.add_log(
                    "INFO",
                    f"Blocked user {user.first_name} ({user_id}) for exceeding PM limit",
                    user_id=user_id
                )
                
                # Notify log chat if configured
                if config_ref.LOG_CHAT_ID:
                    await client_ref.send_message(
                        config_ref.LOG_CHAT_ID,
                        f"🚫 **User Blocked**\n\n"
                        f"**Name:** {user.first_name}\n"
                        f"**Username:** @{user.username or 'None'}\n"
                        f"**ID:** `{user_id}`\n"
                        f"**Reason:** Exceeded PM permit limit ({warnings} warnings)"
                    )
            except Exception as e:
                await db_ref.add_log("ERROR", f"Failed to block user {user_id}: {e}")
        
    except Exception as e:
        await db_ref.add_log("ERROR", f"Error handling unapproved user: {e}")

@message_handler(filters.command("approve", ".") & filters.me)
async def approve_command(client, message: Message):
    """Approve a user for PM"""
    try:
        # Get target user
        target_user = None
        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            # Try to get user by username or ID
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
            await message.edit("❌ **Usage:** `.approve <user_id/@username>` or reply to a message")
            return
        
        if not target_user:
            await message.edit("❌ **Error:** Could not identify user")
            return
        
        # Approve the user
        success = await db_ref.approve_pm(target_user.id, message.from_user.id)
        
        if success:
            # Send approval message
            try:
                await client.send_message(
                    target_user.id,
                    "✅ **You have been approved for PM!**\n\n"
                    "You can now send messages freely."
                )
            except:
                pass
            
            await message.edit(
                f"✅ **User Approved**\n\n"
                f"**Name:** {target_user.first_name}\n"
                f"**Username:** @{target_user.username or 'None'}\n"
                f"**ID:** `{target_user.id}`"
            )
            
            # Log the approval
            await db_ref.add_log(
                "INFO",
                f"Approved user {target_user.first_name} ({target_user.id})",
                user_id=target_user.id
            )
        else:
            await message.edit("❌ **Error:** Failed to approve user")
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("disapprove", ".") & filters.me)
async def disapprove_command(client, message: Message):
    """Disapprove a user for PM"""
    try:
        # Get target user (similar logic to approve)
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
            await message.edit("❌ **Usage:** `.disapprove <user_id/@username>` or reply to a message")
            return
        
        if not target_user:
            await message.edit("❌ **Error:** Could not identify user")
            return
        
        # Disapprove the user
        success = await db_ref.disapprove_pm(target_user.id)
        
        if success:
            await message.edit(
                f"❌ **User Disapproved**\n\n"
                f"**Name:** {target_user.first_name}\n"
                f"**Username:** @{target_user.username or 'None'}\n"
                f"**ID:** `{target_user.id}`"
            )
            
            # Log the disapproval
            await db_ref.add_log(
                "INFO",
                f"Disapproved user {target_user.first_name} ({target_user.id})",
                user_id=target_user.id
            )
        else:
            await message.edit("❌ **Error:** Failed to disapprove user")
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("block", ".") & filters.me)
async def block_command(client, message: Message):
    """Block a user"""
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
            await message.edit("❌ **Usage:** `.block <user_id/@username>` or reply to a message")
            return
        
        if not target_user:
            await message.edit("❌ **Error:** Could not identify user")
            return
        
        # Block the user
        await client.block_user(target_user.id)
        
        await message.edit(
            f"🚫 **User Blocked**\n\n"
            f"**Name:** {target_user.first_name}\n"
            f"**Username:** @{target_user.username or 'None'}\n"
            f"**ID:** `{target_user.id}`"
        )
        
        # Log the block
        await db_ref.add_log(
            "INFO",
            f"Blocked user {target_user.first_name} ({target_user.id})",
            user_id=target_user.id
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("unblock", ".") & filters.me)
async def unblock_command(client, message: Message):
    """Unblock a user"""
    try:
        if len(message.command) < 2:
            await message.edit("❌ **Usage:** `.unblock <user_id/@username>`")
            return
        
        user_input = message.command[1]
        try:
            if user_input.startswith('@'):
                target_user = await client.get_users(user_input)
            else:
                target_user = await client.get_users(int(user_input))
        except:
            await message.edit("❌ **Error:** User not found")
            return
        
        # Unblock the user
        await client.unblock_user(target_user.id)
        
        await message.edit(
            f"✅ **User Unblocked**\n\n"
            f"**Name:** {target_user.first_name}\n"
            f"**Username:** @{target_user.username or 'None'}\n"
            f"**ID:** `{target_user.id}`"
        )
        
        # Log the unblock
        await db_ref.add_log(
            "INFO",
            f"Unblocked user {target_user.first_name} ({target_user.id})",
            user_id=target_user.id
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("pmguard", ".") & filters.me)
async def pmguard_command(client, message: Message):
    """Toggle PM permit on/off"""
    try:
        if len(message.command) > 1:
            action = message.command[1].lower()
            if action in ['on', 'enable', 'true']:
                config_ref.PM_PERMIT_ENABLED = True
                status = "enabled"
            elif action in ['off', 'disable', 'false']:
                config_ref.PM_PERMIT_ENABLED = False
                status = "disabled"
            else:
                await message.edit("❌ **Usage:** `.pmguard [on/off]`")
                return
        else:
            # Toggle current state
            config_ref.PM_PERMIT_ENABLED = not config_ref.PM_PERMIT_ENABLED
            status = "enabled" if config_ref.PM_PERMIT_ENABLED else "disabled"
        
        # Save setting to database
        await db_ref.set_plugin_setting(
            "pm_permit",
            "enabled",
            str(config_ref.PM_PERMIT_ENABLED).lower()
        )
        
        status_emoji = "🟢" if config_ref.PM_PERMIT_ENABLED else "🔴"
        await message.edit(
            f"{status_emoji} **PM Guard {status.title()}**\n\n"
            f"**Status:** {'Active' if config_ref.PM_PERMIT_ENABLED else 'Inactive'}\n"
            f"**Warning Limit:** {config_ref.PM_PERMIT_LIMIT}"
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

async def cleanup_plugin():
    """Cleanup when plugin is unloaded"""
    global warned_users
    warned_users.clear()
