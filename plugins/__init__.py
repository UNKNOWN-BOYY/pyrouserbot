"""
Plugins package for UserBot
Contains all plugin modules
"""

# Plugin information
__version__ = "1.0.0"
__author__ = "UserBot"
__description__ = "UserBot plugins collection"

# Available plugins
AVAILABLE_PLUGINS = [
    "alive",
    "pm_permit", 
    "ping",
    "info",
    "stats",
    "utils"
]

# Plugin categories
PLUGIN_CATEGORIES = {
    "core": ["alive", "ping"],
    "moderation": ["pm_permit"],
    "information": ["info", "stats"],
    "utilities": ["utils"]
}
