"""
Plugin loader system for UserBot
Handles dynamic loading and management of plugins
"""

import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from pyrogram import Client, filters
from pyrogram.types import Message

from database import Database
from config import Config

logger = logging.getLogger(__name__)

class PluginLoader:
    """Plugin loader and manager"""
    
    def __init__(self, client: Client, db: Database, config: Config):
        self.client = client
        self.db = db
        self.config = config
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_handlers: Dict[str, List] = {}
        self.plugins_dir = Path("plugins")
    
    async def load_all_plugins(self):
        """Load all plugins from plugins directory"""
        if not self.plugins_dir.exists():
            logger.warning("Plugins directory not found")
            return
        
        plugin_files = [
            f.stem for f in self.plugins_dir.glob("*.py") 
            if f.stem != "__init__" and not f.stem.startswith("_")
        ]
        
        loaded_count = 0
        for plugin_name in plugin_files:
            if self.config.is_plugin_disabled(plugin_name):
                logger.info(f"Plugin {plugin_name} is disabled")
                continue
                
            if await self.load_plugin(plugin_name):
                loaded_count += 1
        
        logger.info(f"Loaded {loaded_count}/{len(plugin_files)} plugins")
    
    async def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        try:
            # Import the plugin module
            module_path = f"plugins.{plugin_name}"
            
            # Remove from cache if already loaded
            if module_path in sys.modules:
                del sys.modules[module_path]
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Initialize plugin if it has an init function
            if hasattr(module, 'init_plugin'):
                await module.init_plugin(self.client, self.db, self.config)
            
            # Register handlers
            await self._register_plugin_handlers(plugin_name, module)
            
            # Store plugin reference
            self.loaded_plugins[plugin_name] = module
            
            logger.info(f"Plugin loaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        try:
            if plugin_name not in self.loaded_plugins:
                return False
            
            # Remove handlers
            if plugin_name in self.plugin_handlers:
                for handler in self.plugin_handlers[plugin_name]:
                    self.client.remove_handler(*handler)
                del self.plugin_handlers[plugin_name]
            
            # Cleanup plugin if it has a cleanup function
            module = self.loaded_plugins[plugin_name]
            if hasattr(module, 'cleanup_plugin'):
                await module.cleanup_plugin()
            
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]
            
            # Remove from module cache
            module_path = f"plugins.{plugin_name}"
            if module_path in sys.modules:
                del sys.modules[module_path]
            
            logger.info(f"Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        if plugin_name in self.loaded_plugins:
            await self.unload_plugin(plugin_name)
        return await self.load_plugin(plugin_name)
    
    async def _register_plugin_handlers(self, plugin_name: str, module):
        """Register handlers from a plugin module"""
        handlers = []
        
        # Look for handler functions in the module
        for name, obj in inspect.getmembers(module):
            if inspect.iscoroutinefunction(obj) and hasattr(obj, '_handler_info'):
                handler_info = obj._handler_info
                
                # Create the handler
                handler = (
                    getattr(self.client, handler_info['handler_type']),
                    handler_info['filters']
                )
                
                # Add the handler
                self.client.add_handler(handler[0](handler_info['filters'])(obj))
                handlers.append(handler)
        
        if handlers:
            self.plugin_handlers[plugin_name] = handlers
    
    async def unload_all_plugins(self):
        """Unload all loaded plugins"""
        plugin_names = list(self.loaded_plugins.keys())
        for plugin_name in plugin_names:
            await self.unload_plugin(plugin_name)
        logger.info("All plugins unloaded")
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names"""
        return list(self.loaded_plugins.keys())
    
    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if a plugin is loaded"""
        return plugin_name in self.loaded_plugins
    
    async def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a plugin"""
        if plugin_name not in self.loaded_plugins:
            return None
        
        module = self.loaded_plugins[plugin_name]
        
        info = {
            'name': plugin_name,
            'loaded': True,
            'handlers': len(self.plugin_handlers.get(plugin_name, [])),
        }
        
        # Add plugin metadata if available
        if hasattr(module, '__plugin_info__'):
            info.update(module.__plugin_info__)
        
        return info

# Decorator for plugin handlers
def handler(handler_type: str, filters_obj):
    """Decorator to mark plugin handler functions"""
    def decorator(func):
        func._handler_info = {
            'handler_type': handler_type,
            'filters': filters_obj
        }
        return func
    return decorator

# Convenience decorators
def message_handler(filters_obj):
    """Decorator for message handlers"""
    return handler('on_message', filters_obj)

def callback_handler(filters_obj):
    """Decorator for callback handlers"""
    return handler('on_callback_query', filters_obj)

def inline_handler(filters_obj):
    """Decorator for inline handlers"""
    return handler('on_inline_query', filters_obj)
