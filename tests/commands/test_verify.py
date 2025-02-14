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
    
    args = parser.parse_args([
        '--quasar-version', '2.16.9',
        '--vue-version', '3.4.38',
        '--output', 'report.md'
    ])
    assert args.quasar_version == '2.16.9'
    assert args.vue_version == '3.4.38'
    assert args.output == 'report.md'


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('os.path.exists')
@patch('os.path.join')
def test_verify_command_single_component(mock_join, mock_exists, mock_verify, verify_command, capsys):
    """Test verify command with a single component."""
    # Set up mocks
    mock_exists.return_value = True
    mock_join.side_effect = lambda *args: '/'.join(args)
    mock_verify.return_value = {
        'button.json': []  # No issues
    }
    
    # Create args
    args = argparse.Namespace(
        components="ui.button",
        quasar_version="2.16.9",
        vue_version="3.4.38",
        output=None
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "All components verified successfully!" in captured.out
    
    # Verify mock calls
    mock_verify.assert_called_once()
    assert mock_verify.call_args[1]['quasar_version'] == '2.16.9'
    assert mock_verify.call_args[1]['vue_version'] == '3.4.38'


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('os.path.exists')
@patch('os.path.join')
def test_verify_command_with_issues(mock_join, mock_exists, mock_verify, verify_command, capsys):
    """Test verify command when issues are found."""
    # Set up mocks
    mock_exists.return_value = True
    mock_join.side_effect = lambda *args: '/'.join(args)
    mock_verify.return_value = {
        'button.json': ['Missing property "color"', 'Invalid type for "size"']
    }
    
    # Create args
    args = argparse.Namespace(
        components="ui.button",
        quasar_version="2.16.9",
        vue_version="3.4.38",
        output=None
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "Found 2 issues" in captured.out


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('os.path.exists')
@patch('os.path.join')
@patch('builtins.open', new_callable=unittest.mock.mock_open)
def test_verify_command_with_output_file(mock_open, mock_join, mock_exists, mock_verify, verify_command, tmp_path):
    """Test verify command writing to output file."""
    # Set up mocks
    mock_exists.return_value = True
    mock_join.side_effect = lambda *args: '/'.join(args)
    mock_verify.return_value = {
        'button.json': ['Missing property "color"']
    }
    
    # Create args
    args = argparse.Namespace(
        components="ui.button",
        quasar_version="2.16.9",
        vue_version="3.4.38",
        output=str(tmp_path / "report.md")
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Verify file write
    mock_open.assert_called_once_with(str(tmp_path / "report.md"), 'w')
    handle = mock_open()
    assert any("Missing property" in str(call) for call in handle.write.call_args_list)


@patch('nicegui_atlas.commands.verify.verify_components')
@patch('os.path.exists')
@patch('os.path.join')
@patch('os.listdir')
def test_verify_command_all_components(mock_listdir, mock_join, mock_exists, mock_verify, verify_command, capsys):
    """Test verify command with no specific components (verify all)."""
    # Set up mocks
    mock_exists.return_value = True
    mock_join.side_effect = lambda *args: '/'.join(args)
    mock_listdir.return_value = ['button.json', 'checkbox.json', 'categories.json']
    mock_verify.return_value = {
        'button.json': [],
        'checkbox.json': []
    }
    
    # Create args
    args = argparse.Namespace(
        components=None,
        quasar_version="2.16.9",
        vue_version="3.4.38",
        output=None
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
@patch('os.path.exists')
@patch('os.path.join')
def test_verify_command_component_not_found(mock_join, mock_exists, mock_verify, verify_command, capsys):
    """Test verify command when component is not found."""
    # Set up mocks
    mock_exists.return_value = False
    mock_join.side_effect = lambda *args: '/'.join(args)
    
    # Create args
    args = argparse.Namespace(
        components="ui.nonexistent",
        quasar_version="2.16.9",
        vue_version="3.4.38",
        output=None
    )
    
    # Execute command
    verify_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "No component files found to verify" in captured.out
    
    # Verify verify_components was not called
    mock_verify.assert_not_called()
