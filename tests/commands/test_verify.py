"""Tests for the verify command plugin."""

import argparse
import os
import unittest.mock
import pytest
from unittest.mock import Mock, patch
from nicegui_atlas.commands.verify import VerifyCommand


@pytest.fixture
def verify_command():
    """Create an instance of the verify command."""
    return VerifyCommand()


def test_verify_command_properties(verify_command):
    """Test verify command basic properties."""
    assert verify_command.name == "verify"
    assert verify_command.help == "Verify component properties against Quasar documentation"
    assert len(verify_command.examples) > 0


def test_verify_command_parser_setup():
    """Test verify command argument parser setup."""
    cmd = VerifyCommand()
    parser = argparse.ArgumentParser()
    cmd.setup_parser(parser)
    
    args = parser.parse_args(['--output', 'report.md'])
    assert args.output == 'report.md'


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('nicegui_atlas.commands.verify.ComponentFinder')
def test_verify_command_single_component(mock_finder_class, mock_verify, verify_command, capsys):
    """Test verify command with a single component."""
    # Set up mocks
    mock_finder = mock_finder_class.return_value
    mock_finder.find_by_name.return_value = ['db/basic_elements/button.json']
    mock_verify.return_value = {
        'button.json': []  # No issues
    }
    
    # Create args
    args = argparse.Namespace(
        component="ui.button",
        output=None
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "All components verified successfully!" in captured.out
    
    # Verify mock calls
    mock_verify.assert_called_once()


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('nicegui_atlas.commands.verify.ComponentFinder')
def test_verify_command_with_issues(mock_finder_class, mock_verify, verify_command, capsys):
    """Test verify command when issues are found."""
    # Set up mocks
    mock_finder = mock_finder_class.return_value
    mock_finder.find_by_name.return_value = ['db/basic_elements/button.json']
    mock_verify.return_value = {
        'button.json': ['Missing property "color"', 'Invalid type for "size"']
    }
    
    # Create args
    args = argparse.Namespace(
        component="ui.button",
        output=None
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "Found 2 issues" in captured.out


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('nicegui_atlas.commands.verify.ComponentFinder')
@patch('builtins.open', new_callable=unittest.mock.mock_open)
def test_verify_command_with_output_file(mock_open, mock_finder_class, mock_verify, verify_command, tmp_path):
    """Test verify command writing to output file."""
    # Set up mock for both file operations
    mapping_content = '{"ui.button": "db/basic_elements/button.json"}'
    mock_mapping_file = unittest.mock.mock_open(read_data=mapping_content)
    mock_report_file = unittest.mock.mock_open()
    
    def side_effect(filename, mode='r'):
        if str(filename).endswith('component_mappings.json'):
            return mock_mapping_file(filename, mode)
        return mock_report_file(filename, mode)
    
    mock_open.side_effect = side_effect
    # Set up mocks
    mock_finder = mock_finder_class.return_value
    mock_finder.find_by_name.return_value = ['db/basic_elements/button.json']
    mock_verify.return_value = {
        'button.json': ['Missing property "color"']
    }
    
    # Create args
    args = argparse.Namespace(
        component="ui.button",
        output=str(tmp_path / "report.md")
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Verify file operations
    # Verify the report file was opened for writing
    assert any(call == unittest.mock.call(str(tmp_path / "report.md"), 'w') 
              for call in mock_open.call_args_list)
    
    # Verify the report content was written
    report_handle = mock_report_file()
    assert any("Missing property" in str(call) 
              for call in report_handle.write.call_args_list)


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('nicegui_atlas.commands.verify.ComponentFinder')
def test_verify_command_all_components(mock_finder_class, mock_verify, verify_command, capsys):
    """Test verify command with no specific components (verify all)."""
    # Set up mocks
    mock_finder = mock_finder_class.return_value
    mock_finder.find_all.return_value = [
        'db/basic_elements/button.json',
        'db/basic_elements/checkbox.json'
    ]
    mock_verify.return_value = {
        'button.json': [],
        'checkbox.json': []
    }
    
    # Create args with all required attributes
    args = argparse.Namespace(
        component=None,
        filter=None,  # Add filter attribute with default value
        output=None,
        all=True
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "All components verified successfully!" in captured.out
    
    # Verify that categories.json was excluded
    paths = mock_verify.call_args[0][0]
    assert not any('categories.json' in path for path in paths)
    assert not any('template.json' in path for path in paths)


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('nicegui_atlas.commands.verify.ComponentFinder')
def test_verify_command_component_not_found(mock_finder_class, mock_verify, verify_command, capsys):
    """Test verify command when component is not found."""
    # Set up mocks
    mock_finder = mock_finder_class.return_value
    mock_finder.find_by_name.return_value = []
    
    # Create args
    args = argparse.Namespace(
        component="ui.nonexistent",
        output=None
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "No component files found matching 'ui.nonexistent'" in captured.out
    
    # Verify verify_components was not called
    mock_verify.assert_not_called()
