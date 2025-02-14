"""Tests for the command plugin base system."""

import argparse
import pytest
from nicegui_atlas.commands.base import CommandPlugin, PluginRegistry


class TestPlugin(CommandPlugin):
    """Test plugin implementation."""
    
    @property
    def name(self) -> str:
        return "test"
    
    @property
    def help(self) -> str:
        return "Test plugin"
    
    @property
    def examples(self) -> list[str]:
        return ["Example 1", "Example 2"]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--test-arg', help='Test argument')
    
    def execute(self, args: argparse.Namespace) -> None:
        pass


def test_plugin_registry():
    """Test plugin registration and retrieval."""
    registry = PluginRegistry()
    plugin = TestPlugin()
    
    # Test registration
    registry.register(plugin)
    assert registry.get_plugin("test") == plugin
    
    # Test unknown plugin
    assert registry.get_plugin("unknown") is None
    
    # Test getting all plugins
    assert registry.get_all_plugins() == [plugin]


def test_plugin_examples():
    """Test plugin example handling."""
    registry = PluginRegistry()
    plugin = TestPlugin()
    registry.register(plugin)
    
    examples = registry.get_examples()
    assert len(examples) == 2
    assert "Example 1" in examples
    assert "Example 2" in examples


def test_plugin_parser_setup():
    """Test plugin argument parser setup."""
    registry = PluginRegistry()
    plugin = TestPlugin()
    registry.register(plugin)
    
    # Create main parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    
    # Set up plugin parsers
    registry.setup_parsers(subparsers)
    
    # Parse test arguments
    args = parser.parse_args(['test', '--test-arg', 'value'])
    assert args.command == 'test'
    assert args.test_arg == 'value'


def test_plugin_properties():
    """Test plugin property access."""
    plugin = TestPlugin()
    assert plugin.name == "test"
    assert plugin.help == "Test plugin"
    assert len(plugin.examples) == 2
