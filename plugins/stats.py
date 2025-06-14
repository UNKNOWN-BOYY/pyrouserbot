"""
Stats plugin for UserBot
Usage statistics and analytics
"""

from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import Message

from plugin_loader import message_handler

# Plugin info
__plugin_info__ = {
    'name': 'Stats',
    'description': 'Usage statistics and analytics',
    'version': '1.0.0', 
    'commands': ['stats', 'mystats', 'topcmds', 'usage']
}

# Global variables
client_ref = None
db_ref = None
config_ref = None

async def init_plugin(client, db, config):
    """Initialize the stats plugin"""
    global client_ref, db_ref, config_ref
    client_ref = client
    db_ref = db
    config_ref = config

@message_handler(filters.command("stats", ".") & filters.me)
async def stats_command(client, message: Message):
    """Show general bot statistics"""
    try:
        stats_text = f"📊 **Bot Statistics**\n\n"
        
        # Get total users
        total_users = await db_ref.fetch_query("SELECT COUNT(*) as count FROM user_stats")
        if total_users:
            stats_text += f"**Total Users:** {total_users[0]['count']:,}\n"
        
        # Get total messages
        total_messages = await db_ref.fetch_query("SELECT SUM(total_messages) as total FROM user_stats")
        if total_messages and total_messages[0]['total']:
            stats_text += f"**Total Messages:** {total_messages[0]['total']:,}\n"
        
        # Get total commands
        total_commands = await db_ref.fetch_query("SELECT SUM(commands_used) as total FROM user_stats")
        if total_commands and total_commands[0]['total']:
            stats_text += f"**Total Commands:** {total_commands[0]['total']:,}\n"
        
        # Get PM permit stats
        pm_stats = await db_ref.fetch_query("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN approved = 1 THEN 1 ELSE 0 END) as approved,
                SUM(warnings) as total_warnings
            FROM pm_permits
        """)
        
        if pm_stats and pm_stats[0]['total']:
            pm_data = pm_stats[0]
            stats_text += f"\n**PM Permit:**\n"
            stats_text += f"├ **Total Users:** {pm_data['total']:,}\n"
            stats_text += f"├ **Approved:** {pm_data['approved'] or 0:,}\n"
            stats_text += f"└ **Total Warnings:** {pm_data['total_warnings'] or 0:,}\n"
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_users = await db_ref.fetch_query(
            "SELECT COUNT(*) as count FROM user_stats WHERE last_seen > ?",
            (yesterday,)
        )
        
        if recent_users:
            stats_text += f"\n**Recent Activity (24h):**\n"
            stats_text += f"└ **Active Users:** {recent_users[0]['count']:,}\n"
        
        # Get log entries count
        log_count = await db_ref.fetch_query("SELECT COUNT(*) as count FROM bot_logs")
        if log_count:
            stats_text += f"\n**Bot Logs:** {log_count[0]['count']:,} entries"
        
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

@message_handler(filters.command("mystats", ".") & filters.me)
async def my_stats_command(client, message: Message):
    """Show personal statistics"""
    try:
        user_id = message.from_user.id
        user_stats = await db_ref.get_user_stats(user_id)
        
        stats_text = f"📈 **Your Statistics**\n\n"
        
        if user_stats:
            stats_text += f"**Messages Sent:** {user_stats['total_messages']:,}\n"
            stats_text += f"**Commands Used:** {user_stats['commands_used']:,}\n"
            
            if user_stats['last_seen']:
                stats_text += f"**Last Active:** {user_stats['last_seen']}\n"
            
            if user_stats['created_at']:
                stats_text += f"**First Seen:** {user_stats['created_at']}\n"
        else:
            stats_text += "No statistics available yet.\n"
        
        # Get PM permit info
        pm_permit = await db_ref.get_pm_permit(user_id)
        if pm_permit:
            stats_text += f"\n**PM Permit:**\n"
            stats_text += f"├ **Status:** {'✅ Approved' if pm_permit['approved'] else '❌ Not Approved'}\n"
            stats_text += f"└ **Warnings:** {pm_permit['warnings'] or 0}\n"
        
        # Calculate command usage rate
        if user_stats and user_stats['total_messages'] > 0:
            cmd_rate = (user_stats['commands_used'] / user_stats['total_messages']) * 100
            stats_text += f"\n**Command Usage Rate:** {cmd_rate:.1f}%"
        
        await message.edit(stats_text)
        
        # Log command usage
        await db_ref.update_user_stats(
            user_id,
            message.from_user.username,
            message.from_user.first_name,
            command_count=1
        )
        
    except Exception as e:
        await message.edit(f"❌ **Error:** {str(e)}")

@message_handler(filters.command("topcmds", ".") & filters.me)
async def top_commands_command(client, message: Message):
    """Show top command users"""
    try:
        # Get top users by command usage
        top_users = await db_ref.fetch_query("""
            SELECT username, first_name, commands_used, total_messages
            FROM user_stats 
            WHERE commands_used > 0
            ORDER BY commands_used DESC 
            LIMIT 10
        """)
        
        stats_text = f"🏆 **Top Command Users**\n\n"
        
        if top_users:
            for i, user in enumerate(top_users, 1):
                username = f"@{user['username']}" if user['username'] else user['first_name']
                stats_text += f"**{i}.** {username}\n"
                stats_text += f"    └ Commands: {user['commands_used']:,}"
                if user['total_messages']:
                    rate = (user['commands_used'] / user['total_messages']) * 100
                    stats_text += f" ({rate:.1f}%)"
                stats_text += "\n\n"
        else:
            stats_text += "No command usage data available."
        
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

@message_handler(filters.command("usage", ".") & filters.me)
async def usage_command(client, message: Message):
    """Show detailed usage analytics"""
    try:
        stats_text = f"📊 **Usage Analytics**\n\n"
        
        # Daily stats (last 7 days)
        daily_stats = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # Get daily activity
            day_users = await db_ref.fetch_query("""
                SELECT COUNT(*) as count FROM user_stats 
                WHERE DATE(last_seen) = ?
            """, (date_str,))
            
            if day_users and day_users[0]['count'] > 0:
                daily_stats.append({
                    'date': date.strftime('%m/%d'),
                    'users': day_users[0]['count']
                })
        
        if daily_stats:
            stats_text += f"**Daily Active Users (Last 7 days):**\n"
            for day in reversed(daily_stats[-5:]):  # Show last 5 days
                stats_text += f"├ {day['date']}: {day['users']} users\n"
        
        # Hour distribution (approximate)
        current_hour = datetime.now().hour
        stats_text += f"\n**Current Hour Activity:**\n"
        stats_text += f"└ Hour {current_hour:02d}:00 - Active now\n"
        
        # Top warning users (PM Permit)
        warning_users = await db_ref.fetch_query("""
            SELECT username, first_name, warnings
            FROM pm_permits 
            WHERE warnings > 0
            ORDER BY warnings DESC 
            LIMIT 5
        """)
        
        if warning_users:
            stats_text += f"\n**Top Warning Users:**\n"
            for user in warning_users:
                name = f"@{user['username']}" if user['username'] else user['first_name']
                stats_text += f"├ {name}: {user['warnings']} warnings\n"
        
        # Recent logs summary
        recent_logs = await db_ref.fetch_query("""
            SELECT level, COUNT(*) as count
            FROM bot_logs 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY level
            ORDER BY count DESC
        """)
        
        if recent_logs:
            stats_text += f"\n**Recent Logs (24h):**\n"
            for log in recent_logs:
                stats_text += f"├ {log['level']}: {log['count']}\n"
        
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

@message_handler(filters.command("analytics", ".") & filters.me)
async def analytics_command(client, message: Message):
    """Show advanced analytics"""
    try:
        stats_text = f"📈 **Advanced Analytics**\n\n"
        
        # Message to command ratio
        total_msgs = await db_ref.fetch_query("SELECT SUM(total_messages) as total FROM user_stats")
        total_cmds = await db_ref.fetch_query("SELECT SUM(commands_used) as total FROM user_stats")
        
        if total_msgs and total_cmds and total_msgs[0]['total'] and total_cmds[0]['total']:
            ratio = (total_cmds[0]['total'] / total_msgs[0]['total']) * 100
            stats_text += f"**Command Usage Rate:** {ratio:.2f}%\n"
            stats_text += f"**Messages per Command:** {total_msgs[0]['total'] / total_cmds[0]['total']:.1f}\n\n"
        
        # User engagement levels
        engagement_levels = await db_ref.fetch_query("""
            SELECT 
                CASE 
                    WHEN commands_used = 0 THEN 'Inactive'
                    WHEN commands_used <= 5 THEN 'Low'
                    WHEN commands_used <= 20 THEN 'Medium'
                    WHEN commands_used <= 50 THEN 'High'
                    ELSE 'Very High'
                END as engagement,
                COUNT(*) as count
            FROM user_stats
            GROUP BY engagement
            ORDER BY count DESC
        """)
        
        if engagement_levels:
            stats_text += f"**User Engagement:**\n"
            for level in engagement_levels:
                stats_text += f"├ {level['engagement']}: {level['count']} users\n"
        
        # PM Permit effectiveness
        pm_effectiveness = await db_ref.fetch_query("""
            SELECT 
                AVG(warnings) as avg_warnings,
                MAX(warnings) as max_warnings,
                COUNT(CASE WHEN approved = 1 THEN 1 END) * 100.0 / COUNT(*) as approval_rate
            FROM pm_permits
        """)
        
        if pm_effectiveness and pm_effectiveness[0]['avg_warnings']:
            pm_data = pm_effectiveness[0]
            stats_text += f"\n**PM Permit Effectiveness:**\n"
            stats_text += f"├ Average Warnings: {pm_data['avg_warnings']:.1f}\n"
            stats_text += f"├ Max Warnings: {pm_data['max_warnings']}\n"
            stats_text += f"└ Approval Rate: {pm_data['approval_rate']:.1f}%\n"
        
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
