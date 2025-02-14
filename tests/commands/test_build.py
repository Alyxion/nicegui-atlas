"""Tests for the build command plugin."""

import argparse
import os
import pytest
from unittest.mock import Mock, patch
from nicegui_atlas.commands.build import BuildCommand


@pytest.fixture
def build_command():
    """Create an instance of the build command."""
    return BuildCommand()


def test_build_command_properties(build_command):
    """Test build command basic properties."""
    assert build_command.name == "build"
    assert build_command.help == "Build component overview in output directory"
    assert len(build_command.examples) > 0


def test_build_command_parser_setup():
    """Test build command argument parser setup."""
    cmd = BuildCommand()
    parser = argparse.ArgumentParser()
    cmd.setup_parser(parser)
    
    # Build command doesn't add any arguments, but should parse without error
    args = parser.parse_args([])
    assert isinstance(args, argparse.Namespace)


@patch('nicegui_atlas.commands.build.IndexCommand')
@patch('os.makedirs')
def test_build_command_execution(mock_makedirs, mock_index_cmd, build_command, capsys):
    """Test build command basic execution."""
    # Set up mock index command
    mock_index_instance = Mock()
    mock_index_cmd.return_value = mock_index_instance
    
    # Create args
    args = argparse.Namespace()
    
    # Execute command
    build_command.execute(args)
    
    # Verify output directory was created
    mock_makedirs.assert_called_once()
    assert mock_makedirs.call_args[1]['exist_ok'] is True
    
    # Verify index command was called with correct args
    mock_index_instance.execute.assert_called_once()
    call_args = mock_index_instance.execute.call_args[0][0]
    assert call_args.quiet is True
    assert call_args.output.endswith('component_overview.md')
    
    # Check output message
    captured = capsys.readouterr()
    assert "Component overview built in" in captured.out


@patch('nicegui_atlas.commands.build.IndexCommand')
@patch('os.makedirs')
def test_build_command_output_path(mock_makedirs, mock_index_cmd, build_command):
    """Test build command output path construction."""
    # Set up mock index command
    mock_index_instance = Mock()
    mock_index_cmd.return_value = mock_index_instance
    
    # Create args
    args = argparse.Namespace()
    
    # Execute command
    build_command.execute(args)
    
    # Get the output path from the index command call
    call_args = mock_index_instance.execute.call_args[0][0]
    output_path = call_args.output
    
    # Verify path structure
    assert output_path.endswith('output/component_overview.md')
    assert os.path.basename(output_path) == 'component_overview.md'
    assert os.path.dirname(output_path).endswith('output')


@patch('nicegui_atlas.commands.build.IndexCommand')
@patch('os.makedirs')
def test_build_command_directory_creation(mock_makedirs, mock_index_cmd, build_command):
    """Test build command directory creation."""
    # Set up mock index command
    mock_index_instance = Mock()
    mock_index_cmd.return_value = mock_index_instance
    
    # Create args
    args = argparse.Namespace()
    
    # Execute command
    build_command.execute(args)
    
    # Verify directory creation
    mock_makedirs.assert_called_once()
    created_dir = mock_makedirs.call_args[0][0]
    assert os.path.basename(created_dir) == 'output'
    assert mock_makedirs.call_args[1]['exist_ok'] is True


@patch('nicegui_atlas.commands.build.IndexCommand')
@patch('os.makedirs')
def test_build_command_index_args(mock_makedirs, mock_index_cmd, build_command):
    """Test build command index command argument setup."""
    # Set up mock index command
    mock_index_instance = Mock()
    mock_index_cmd.return_value = mock_index_instance
    
    # Create args
    args = argparse.Namespace()
    
    # Execute command
    build_command.execute(args)
    
    # Verify index command arguments
    call_args = mock_index_instance.execute.call_args[0][0]
    assert hasattr(call_args, 'output')
    assert hasattr(call_args, 'quiet')
    assert call_args.quiet is True
