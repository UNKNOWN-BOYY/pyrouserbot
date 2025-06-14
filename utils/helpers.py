"""
Helper functions for UserBot
Common utilities and formatting functions
"""

import platform
import psutil
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

def format_uptime(uptime: timedelta) -> str:
    """Format uptime duration to human readable string"""
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds and not days:  # Only show seconds if less than a day
        parts.append(f"{seconds}s")
    
    return " ".join(parts) if parts else "0s"

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information"""
    try:
        # Basic system info
        system_info = {
            'os': f"{platform.system()} {platform.release()}",
            'python_version': f"{sys.version.split()[0]}",
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or platform.machine(),
        }
        
        # Resource usage with psutil
        try:
            # CPU usage
            system_info['cpu_percent'] = psutil.cpu_percent(interval=1)
            system_info['cpu_count'] = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_info['memory_total'] = format_bytes(memory.total)
            system_info['memory_available'] = format_bytes(memory.available)
            system_info['memory_percent'] = memory.percent
            system_info['memory_used'] = format_bytes(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            system_info['disk_total'] = format_bytes(disk.total)
            system_info['disk_used'] = format_bytes(disk.used)
            system_info['disk_free'] = format_bytes(disk.free)
            system_info['disk_percent'] = (disk.used / disk.total) * 100
            
            # Process info
            process = psutil.Process()
            system_info['process_memory'] = format_bytes(process.memory_info().rss)
            system_info['process_cpu'] = process.cpu_percent()
            system_info['process_threads'] = process.num_threads()
            
        except ImportError:
            # Fallback without psutil
            system_info.update({
                'cpu_percent': 'N/A',
                'memory_percent': 'N/A',
                'disk_percent': 'N/A',
                'memory_available': 'N/A'
            })
        except Exception:
            # Error getting system stats
            system_info.update({
                'cpu_percent': 'Error',
                'memory_percent': 'Error',
                'disk_percent': 'Error',
                'memory_available': 'Error'
            })
        
        return system_info
        
    except Exception as e:
        return {
            'os': 'Unknown',
            'python_version': sys.version.split()[0],
            'error': str(e)
        }

def format_duration(seconds: int) -> str:
    """Format seconds to human readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h" if hours else f"{days}d"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def parse_time_string(time_str: str) -> timedelta:
    """Parse time string like '1h30m' to timedelta"""
    import re
    
    time_regex = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?')
    match = time_regex.match(time_str.lower())
    
    if not match:
        raise ValueError("Invalid time format")
    
    days, hours, minutes, seconds = match.groups()
    
    return timedelta(
        days=int(days or 0),
        hours=int(hours or 0),
        minutes=int(minutes or 0),
        seconds=int(seconds or 0)
    )

def get_chat_type_emoji(chat_type: str) -> str:
    """Get emoji for chat type"""
    chat_emojis = {
        'private': '👤',
        'group': '👥',
        'supergroup': '🏢',
        'channel': '📢',
        'bot': '🤖'
    }
    return chat_emojis.get(chat_type.lower(), '💬')

def format_user_status(status) -> str:
    """Format user status to readable string"""
    status_map = {
        'online': '🟢 Online',
        'offline': '⚫ Offline',
        'recently': '🟡 Recently',
        'last_week': '🟠 Last Week',
        'last_month': '🔴 Last Month',
        'long_ago': '⚪ Long Ago'
    }
    
    if hasattr(status, 'name'):
        return status_map.get(status.name.lower(), '❓ Unknown')
    return status_map.get(str(status).lower(), '❓ Unknown')

def clean_filename(filename: str) -> str:
    """Clean filename for safe file operations"""
    import re
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename or 'unnamed'

def is_admin_user(user_id: int, admin_list: list) -> bool:
    """Check if user is in admin list"""
    return user_id in admin_list

def format_permission_list(permissions) -> list:
    """Format chat permissions to readable list"""
    perm_list = []
    
    if hasattr(permissions, 'can_send_messages') and permissions.can_send_messages:
        perm_list.append("💬 Send Messages")
    if hasattr(permissions, 'can_send_media_messages') and permissions.can_send_media_messages:
        perm_list.append("📷 Send Media")
    if hasattr(permissions, 'can_send_polls') and permissions.can_send_polls:
        perm_list.append("📊 Send Polls")
    if hasattr(permissions, 'can_send_other_messages') and permissions.can_send_other_messages:
        perm_list.append("🎭 Send Stickers")
    if hasattr(permissions, 'can_add_web_page_previews') and permissions.can_add_web_page_previews:
        perm_list.append("🔗 Add Links")
    if hasattr(permissions, 'can_change_info') and permissions.can_change_info:
        perm_list.append("✏️ Change Info")
    if hasattr(permissions, 'can_invite_users') and permissions.can_invite_users:
        perm_list.append("➕ Invite Users")
    
    return perm_list

def get_progress_bar(percentage: float, length: int = 10) -> str:
    """Generate a progress bar string"""
    filled = int(length * percentage / 100)
    empty = length - filled
    return '█' * filled + '░' * empty

def validate_user_input(input_str: str, input_type: str = 'text') -> bool:
    """Validate user input based on type"""
    if input_type == 'user_id':
        try:
            user_id = int(input_str)
            return 0 < user_id < 10**10  # Reasonable range for Telegram user IDs
        except ValueError:
            return False
    
    elif input_type == 'username':
        import re
        return bool(re.match(r'^@?[a-zA-Z][a-zA-Z0-9_]{4,31}$', input_str))
    
    elif input_type == 'command':
        import re
        return bool(re.match(r'^[a-z][a-z0-9_]*$', input_str))
    
    return len(input_str.strip()) > 0

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable string"""
    return format_bytes(size_bytes)

def get_time_ago(timestamp: datetime) -> str:
    """Get human readable time ago string"""
    now = datetime.now()
    if timestamp.tzinfo:
        # If timestamp has timezone info, make now timezone aware
        from datetime import timezone
        now = now.replace(tzinfo=timezone.utc)
    
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"
