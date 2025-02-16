"""Unit tests for the backup command."""

import argparse
import json
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

from nicegui_atlas.commands.backup import Backup, BackupCommand


@pytest.fixture
def mock_env(tmp_path):
    """Create a mock environment for testing."""
    # Create mock NiceGUI path
    nicegui_path = tmp_path / "nicegui"
    elements_path = nicegui_path / "elements"
    elements_path.mkdir(parents=True)
    
    # Create mock component files
    (elements_path / "button.py").write_text("class Button: pass")
    (elements_path / "button.js").write_text("// Button JS")
    
    # Create mock lib files
    lib_path = elements_path / "lib" / "button"
    lib_path.mkdir(parents=True)
    (lib_path / "button.js").write_text("// Button lib")
    
    # Create mock db directory
    db_path = tmp_path / "db" / "basic_elements"
    db_path.mkdir(parents=True)
    
    # Create mock JSON file
    button_json = {
        "name": "nicegui.ui.button",
        "source_path": "elements/button.py",
        "description": "Button component"
    }
    (db_path / "button.json").write_text(json.dumps(button_json))
    
    # Create mock backup directory
    backup_path = tmp_path / "backups"
    backup_path.mkdir()
    
    return {
        "root": tmp_path,
        "nicegui_path": nicegui_path,
        "elements_path": elements_path,
        "db_path": db_path,
        "backup_path": backup_path
    }


def test_backup_initialization(mock_env):
    """Test backup class initialization."""
    backup = Backup(nicegui_path=str(mock_env["nicegui_path"]))
    assert backup.nicegui_path == str(mock_env["nicegui_path"] / "nicegui")
    assert backup.output_dir == "backups"

    backup = Backup(nicegui_path=str(mock_env["nicegui_path"]), output_dir="custom")
    assert backup.output_dir == "custom"


def test_calculate_md5(mock_env):
    """Test MD5 calculation."""
    backup = Backup(nicegui_path=str(mock_env["nicegui_path"]))
    test_file = mock_env["elements_path"] / "button.py"
    
    # Calculate expected MD5
    with open(test_file, "rb") as f:
        import hashlib
        expected_md5 = hashlib.md5(f.read()).hexdigest()
    
    assert backup.calculate_md5(test_file) == expected_md5


def test_get_referenced_files(mock_env):
    """Test getting referenced files from JSON."""
    backup = Backup(nicegui_path=str(mock_env["nicegui_path"]))
    
    with patch("pathlib.Path.cwd", return_value=mock_env["root"]):
        files = backup.get_referenced_files()
        assert "button.py" in files
        assert "button.js" in files


def test_backup_component(mock_env):
    """Test backing up a single component."""
    # Create source files in nicegui/elements
    elements_path = mock_env["nicegui_path"] / "nicegui" / "elements"
    elements_path.mkdir(parents=True, exist_ok=True)
    
    # Create Python file
    (elements_path / "button.py").write_text("class Button: pass")
    # Create JS file
    (elements_path / "button.js").write_text("// Button JS")
    # Create lib file
    lib_path = elements_path / "lib" / "button"
    lib_path.mkdir(parents=True, exist_ok=True)
    (lib_path / "button.js").write_text("// Button lib")
    
    # Create db directory with component JSON
    db_path = mock_env["root"] / "db" / "basic_elements"
    db_path.mkdir(parents=True, exist_ok=True)
    component_data = {
        "name": "nicegui.ui.button",
        "source_path": "elements/button.py",
        "description": "Button component"
    }
    json_path = db_path / "button.json"
    with open(json_path, 'w') as f:
        json.dump(component_data, f)
    
    # Initialize backup
    backup = Backup(
        nicegui_path=str(mock_env["nicegui_path"]),
        output_dir=str(mock_env["backup_path"])
    )
    
    # Execute backup
    with patch("pathlib.Path.cwd", return_value=mock_env["root"]):
        files = backup.get_referenced_files()
        updated_data = backup.backup_component(json_path, component_data, files)
    
    # Check files were backed up
    assert (mock_env["backup_path"] / "elements/button.py").exists()
    assert (mock_env["backup_path"] / "elements/button.js").exists()
    assert (mock_env["backup_path"] / "elements/lib/button/button.js").exists()
    
    # Check checksums were added
    assert "py_checksum" in updated_data
    assert "js_checksum" in updated_data
    assert "lib_checksums" in updated_data


def test_clean_backup_dir(mock_env):
    """Test cleaning backup directory."""
    backup = Backup(
        nicegui_path=str(mock_env["nicegui_path"]),
        output_dir=str(mock_env["backup_path"])
    )
    
    # Create some test files
    test_file = mock_env["backup_path"] / "test.txt"
    test_file.write_text("test")
    test_dir = mock_env["backup_path"] / "test_dir"
    test_dir.mkdir()
    (test_dir / "test.txt").write_text("test")
    
    backup.clean_backup_dir()
    
    # Check directory was cleaned
    assert not test_file.exists()
    assert not test_dir.exists()
    assert mock_env["backup_path"].exists()


def test_backup_command():
    """Test backup command plugin."""
    cmd = BackupCommand()
    
    assert cmd.name == "backup"
    assert cmd.help == "Create backups of NiceGUI component files"
    assert len(cmd.examples) > 0
    
    # Test parser setup
    parser = argparse.ArgumentParser()
    cmd.setup_parser(parser)
    
    args = parser.parse_args(['--output-dir', 'custom_backups', '--clean'])
    assert args.output_dir == 'custom_backups'
    assert args.clean is True
    
    args = parser.parse_args([])  # Test defaults
    assert args.output_dir == 'backups'
    assert args.clean is False


def test_backup_command_execute_with_env_file(mock_env, tmp_path):
    """Test backup command execution with .env file."""
    cmd = BackupCommand()
    args = MagicMock()
    args.output_dir = str(mock_env["backup_path"])
    args.clean = True
    
    # Create mock .env file
    env_file = tmp_path / ".env"
    env_file.write_text(f"NICEGUI_PATH={mock_env['nicegui_path']}")
    
    with patch("pathlib.Path.cwd", return_value=tmp_path):
        cmd.execute(args)
    
    # Check backup was created
    assert (mock_env["backup_path"] / "elements/button.py").exists()


def test_backup_command_execute_without_env_file(mock_env, capsys):
    """Test backup command execution without .env file."""
    cmd = BackupCommand()
    args = MagicMock()
    args.output_dir = str(mock_env["backup_path"])
    args.clean = True

    with patch("pathlib.Path.cwd", return_value=mock_env["root"]):
        with patch("builtins.open", side_effect=FileNotFoundError):
            cmd.execute(args)

    # Check error message
    captured = capsys.readouterr()
    assert "Error loading .env file" in captured.out


def test_backup_command_execute_with_invalid_env(mock_env, tmp_path, capsys):
    """Test backup command execution with invalid .env file."""
    cmd = BackupCommand()
    args = MagicMock()
    args.output_dir = str(mock_env["backup_path"])
    args.clean = True

    # Mock open to return invalid .env content
    mock_env_file = mock_open(read_data="INVALID_ENV_FILE")
    
    with patch("pathlib.Path.cwd", return_value=tmp_path):
        with patch("builtins.open", mock_env_file):
            cmd.execute(args)

    # Check error message
    captured = capsys.readouterr()
    assert "Error loading .env file" in captured.out
