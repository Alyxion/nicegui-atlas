"""Tests for the info command plugin."""

import argparse
import pytest
from unittest.mock import Mock, patch
from nicegui_atlas.commands.info import InfoCommand
from nicegui_atlas.models import (
    ComponentInfo,
    QuasarComponentInfo,
    LibraryInfo,
)


@pytest.fixture
def mock_component():
    """Create a mock component with test data."""
    return ComponentInfo(
            name="nicegui.ui.test_component",
            type="nicegui",  # Required field
            source_path="elements/test.py",
            description="Test component description",
            direct_ancestors=["BaseElement"],
            quasar_components=[
                QuasarComponentInfo(
                    name="QTest",
                    url="https://quasar.dev/components/test"
                )
            ],
            libraries=[
                LibraryInfo(
                    name="test-lib"
                )
            ],
            internal_components=["InternalTest"],
            html_element="div",
            js_file=None,
            properties={},
            events={},
            functions={}
        )


@pytest.fixture
def info_command():
    """Create an instance of the info command."""
    return InfoCommand()


def test_info_command_properties(info_command):
    """Test info command basic properties."""
    assert info_command.name == "info"
    assert info_command.help == "Show information about NiceGUI or Quasar components"
    assert len(info_command.examples) > 0


def test_info_command_parser_setup():
    """Test info command argument parser setup."""
    cmd = InfoCommand()
    parser = argparse.ArgumentParser()
    cmd.setup_parser(parser)
    
    args = parser.parse_args([
        'ui.test',
        '--filter', 'test',
        '--output', 'test.md',
        '--sections', 'properties,events',
        '--quasar'
    ])
    assert args.components == 'ui.test'
    assert args.filter == 'test'
    assert args.output == 'test.md'
    assert args.sections == 'properties,events'
    assert args.quasar is True


@patch('nicegui_atlas.commands.info.registry')
def test_info_command_single_component(mock_registry, info_command, mock_component, capsys):
    """Test info command with a single component."""
    # Set up mock
    mock_registry.get_nicegui_component.return_value = mock_component
    
    # Create args
    args = argparse.Namespace(
        components="ui.test_component",
        filter=None,
        output=None,
        quasar=False,
        sections=None
    )
    
    # Execute command
    info_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "Test component description" in captured.out
    assert "BaseElement" in captured.out
    assert "QTest" in captured.out
    assert "test-lib" in captured.out


@patch('nicegui_atlas.commands.info.registry')
def test_info_command_with_filter(mock_registry, info_command, mock_component, capsys):
    """Test info command with filter."""
    # Set up mock
    mock_registry.get_nicegui_component.return_value = mock_component
    
    # Create args
    args = argparse.Namespace(
        components="ui.test_component",
        filter="test,base",
        output=None,
        quasar=False,
        sections=None
    )
    
    # Execute command
    info_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "Test component description" in captured.out


@patch('nicegui_atlas.commands.info.registry')
def test_info_command_with_output_file(mock_registry, info_command, mock_component, tmp_path):
    """Test info command writing to output file."""
    # Set up mock
    mock_registry.get_nicegui_component.return_value = mock_component
    
    # Create output file path
    output_file = tmp_path / "test_output.md"
    
    # Create args
    args = argparse.Namespace(
        components="ui.test_component",
        filter=None,
        output=str(output_file),
        quasar=False,
        sections=None
    )
    
    # Execute command
    info_command.execute(args)
    
    # Check file contents
    assert output_file.exists()
    content = output_file.read_text()
    assert "Test component description" in content
    assert "BaseElement" in content
    assert "QTest" in content
    assert "test-lib" in content


@patch('nicegui_atlas.commands.info.registry')
def test_info_command_no_components_found(mock_registry, info_command, capsys):
    """Test info command when no components are found."""
    # Set up mock to return None
    mock_registry.get_nicegui_component.return_value = None
    
    # Create args
    args = argparse.Namespace(
        components="ui.nonexistent",
        filter=None,
        output=None,
        quasar=False,
        sections=None
    )
    
    # Execute command
    info_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "No components found matching the criteria" in captured.out


@patch('nicegui_atlas.commands.info.registry')
def test_info_command_multiple_components(mock_registry, info_command, mock_component, capsys):
    """Test info command with multiple components."""
    # Set up mock to return the same component for different names
    mock_registry.get_nicegui_component.return_value = mock_component
    
    # Create args
    args = argparse.Namespace(
        components="ui.test_component;ui.other_component",
        filter=None,
        output=None,
        quasar=False,
        sections=None
    )
    
    # Execute command
    info_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert captured.out.count("Test component description") == 2
