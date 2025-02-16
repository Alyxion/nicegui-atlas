"""Tests for the index command plugin."""

import argparse
import pytest
from unittest.mock import Mock, patch
from nicegui_atlas.commands.index import IndexCommand


@pytest.fixture
def mock_category():
    """Create a mock category with test data."""
    return Mock(
        id="test_category",
        name="Test Category",
        description="Test category description"
    )


@pytest.fixture
def mock_component():
    """Create a mock component with test data."""
    component = Mock(
        source_path="test.py",
        description="Test component description",
        direct_ancestors=["BaseElement"],
        quasar_components=["QTest"],  # Changed to match implementation
        libraries=[{"name": "test-lib"}],
        internal_components=["InternalTest"],
        html_element="div",
        js_file=None
    )
    # Add name attribute that can be used for sorting
    component.name = "nicegui.ui.test_component"
    return component


@pytest.fixture
def index_command():
    """Create an instance of the index command."""
    return IndexCommand()


def test_index_command_properties(index_command):
    """Test index command basic properties."""
    assert index_command.name == "index"
    assert index_command.help == "Generate full component documentation"
    assert len(index_command.examples) > 0


def test_index_command_parser_setup():
    """Test index command argument parser setup."""
    cmd = IndexCommand()
    parser = argparse.ArgumentParser()
    cmd.setup_parser(parser)
    
    args = parser.parse_args(['--output', 'test.md', '--quiet'])
    assert args.output == 'test.md'
    assert args.quiet is True


@patch('nicegui_atlas.commands.index.ComponentAtlas')
def test_index_command_basic_output(mock_atlas, index_command, mock_category, mock_component, capsys):
    """Test index command basic output generation."""
    # Set up mocks
    mock_atlas.get_categories.return_value = [mock_category]
    mock_atlas.get_category.return_value = [mock_component]
    
    # Create args
    args = argparse.Namespace(
        output=None,
        quiet=False
    )
    
    # Execute command
    index_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "NiceGUI UI Components" in captured.out
    assert "Test Category" in captured.out
    assert "Test category description" in captured.out
    assert "Test component description" in captured.out
    assert "BaseElement" in captured.out
    assert "QTest" in captured.out
    assert "test-lib" in captured.out


@patch('nicegui_atlas.commands.index.ComponentAtlas')
def test_index_command_with_output_file(mock_atlas, index_command, mock_category, mock_component, tmp_path):
    """Test index command writing to output file."""
    # Set up mocks
    mock_atlas.get_categories.return_value = [mock_category]
    mock_atlas.get_category.return_value = [mock_component]
    
    # Create output file path
    output_file = tmp_path / "test_output.md"
    
    # Create args
    args = argparse.Namespace(
        output=str(output_file),
        quiet=True
    )
    
    # Execute command
    index_command.execute(args)
    
    # Check file contents
    assert output_file.exists()
    content = output_file.read_text()
    assert "NiceGUI UI Components" in content
    assert "Test Category" in content
    assert "Test category description" in content
    assert "Test component description" in content
    assert "BaseElement" in content
    assert "QTest" in content
    assert "test-lib" in content


@patch('nicegui_atlas.commands.index.ComponentAtlas')
def test_index_command_empty_category(mock_atlas, index_command, mock_category, capsys):
    """Test index command with empty category."""
    # Set up mocks
    mock_atlas.get_categories.return_value = [mock_category]
    mock_atlas.get_category.return_value = []  # Empty category
    
    # Create args
    args = argparse.Namespace(
        output=None,
        quiet=False
    )
    
    # Execute command
    index_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "Test Category" in captured.out
    assert "Test category description" in captured.out


@patch('nicegui_atlas.commands.index.ComponentAtlas')
def test_index_command_multiple_components(mock_atlas, index_command, mock_category, mock_component, capsys):
    """Test index command with multiple components in category."""
    # Create second component with a different name for sorting
    second_component = Mock(
        source_path="other.py",
        description="Other component description",
        direct_ancestors=["BaseElement"],
        quasar_components=[],
        libraries=[],
        internal_components=[],
        html_element="div",
        js_file=None
    )
    second_component.name = "nicegui.ui.other_component"
    
    # Set up mocks
    mock_atlas.get_categories.return_value = [mock_category]
    mock_atlas.get_category.return_value = [mock_component, second_component]
    
    # Create args
    args = argparse.Namespace(
        output=None,
        quiet=False
    )
    
    # Execute command
    index_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "Test component description" in captured.out
    assert "Other component description" in captured.out
