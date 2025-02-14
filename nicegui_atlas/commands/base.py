"""Base classes for command plugins."""

from abc import ABC, abstractmethod
import argparse
from typing import Optional, List


class CommandPlugin(ABC):
    """Base class for command plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name used in CLI."""
        pass
    
    @property
    @abstractmethod
    def help(self) -> str:
        """Help text for the command."""
        pass
    
    @property
    def examples(self) -> List[str]:
        """Example usages of the command."""
        return []
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        """Set up command-specific arguments.
        
        Override this method to add custom arguments.
        """
        pass
    
    @abstractmethod
    def execute(self, args: argparse.Namespace) -> None:
        """Execute the command with given arguments."""
        pass


class PluginRegistry:
    """Registry for command plugins."""
    
    def __init__(self):
        self._plugins: dict[str, CommandPlugin] = {}
    
    def register(self, plugin: CommandPlugin) -> None:
        """Register a command plugin."""
        self._plugins[plugin.name] = plugin
    
    def get_plugin(self, name: str) -> Optional[CommandPlugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)
    
    def get_all_plugins(self) -> List[CommandPlugin]:
        """Get all registered plugins."""
        return list(self._plugins.values())
    
    def setup_parsers(self, subparsers: argparse._SubParsersAction) -> None:
        """Set up parsers for all registered plugins."""
        for plugin in self._plugins.values():
            parser = subparsers.add_parser(plugin.name, help=plugin.help)
            plugin.setup_parser(parser)
    
    def get_examples(self) -> List[str]:
        """Get examples from all plugins."""
        examples = []
        for plugin in self._plugins.values():
            examples.extend(plugin.examples)
        return examples


# Global plugin registry
registry = PluginRegistry()
