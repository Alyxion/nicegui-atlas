"""Tests for the qinfo command plugin."""

import argparse
import pytest
from unittest.mock import patch, MagicMock
from nicegui_atlas.commands.qinfo import QInfoCommand, get_component_info


@pytest.fixture
def qinfo_command():
    """Create an instance of the qinfo command."""
    return QInfoCommand()


def test_qinfo_command_properties(qinfo_command):
    """Test qinfo command basic properties."""
    assert qinfo_command.name == "qinfo"
    assert qinfo_command.help == "Get information about Quasar components"
    assert len(qinfo_command.examples) > 0


def test_qinfo_command_parser_setup():
    """Test qinfo command argument parser setup."""
    cmd = QInfoCommand()
    parser = argparse.ArgumentParser()
    cmd.setup_parser(parser)
    
    args = parser.parse_args(['QBtn'])
    assert args.components == ['QBtn']
    assert args.sections is None
    
    args = parser.parse_args(['QBtn', '--sections', 'properties', 'events'])
    assert args.components == ['QBtn']
    assert args.sections == ['properties', 'events']


@patch('nicegui_atlas.commands.qinfo.get_cached_web_types')
def test_qinfo_command_single_component(mock_get_web_types, qinfo_command, capsys):
    """Test qinfo command with a single component."""
    # Mock web-types data
    mock_get_web_types.return_value = {
        'contributions': {
            'html': {
                'tags': [{
                    'name': 'QBtn',
                    'attributes': [{
                        'name': 'color',
                        'description': 'Color name for component',
                        'value': {'type': 'string'},
                        'doc-url': 'https://quasar.dev/vue-components/button'
                    }],
                    'events': [{
                        'name': 'click',
                        'description': 'Emitted when clicked',
                        'arguments': [{
                            'name': 'evt',
                            'type': 'Event',
                            'description': 'JS event object'
                        }]
                    }]
                }]
            }
        }
    }
    
    # Execute command
    args = argparse.Namespace(
        components=['QBtn'],
        sections=None
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "=== QBtn ===" in captured.out
    assert "Documentation: https://quasar.dev/vue-components/button" in captured.out
    assert "color (string): Color name for component" in captured.out
    assert "click: Emitted when clicked" in captured.out
    assert "evt (Event): JS event object" in captured.out


@patch('nicegui_atlas.commands.qinfo.get_cached_web_types')
def test_qinfo_command_without_q_prefix(mock_get_web_types, qinfo_command, capsys):
    """Test qinfo command with component name without Q prefix."""
    # Mock web-types data
    mock_get_web_types.return_value = {
        'contributions': {
            'html': {
                'tags': [{
                    'name': 'QBtn',
                    'attributes': [{
                        'name': 'color',
                        'description': 'Color name for component',
                        'value': {'type': 'string'}
                    }]
                }]
            }
        }
    }
    
    # Execute command
    args = argparse.Namespace(
        components=['Btn'],
        sections=None
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "=== QBtn ===" in captured.out
    assert "color (string): Color name for component" in captured.out


@patch('nicegui_atlas.commands.qinfo.get_cached_web_types')
def test_qinfo_command_with_sections(mock_get_web_types, qinfo_command, capsys):
    """Test qinfo command with specific sections."""
    # Mock web-types data
    mock_get_web_types.return_value = {
        'contributions': {
            'html': {
                'tags': [{
                    'name': 'QBtn',
                    'attributes': [{
                        'name': 'color',
                        'description': 'Color name for component',
                        'value': {'type': 'string'}
                    }],
                    'events': [{
                        'name': 'click',
                        'description': 'Emitted when clicked',
                        'arguments': []
                    }]
                }]
            }
        }
    }
    
    # Test properties only
    args = argparse.Namespace(
        components=['QBtn'],
        sections=['properties']
    )
    qinfo_command.execute(args)
    captured = capsys.readouterr()
    assert "Properties:" in captured.out
    assert "color (string): Color name for component" in captured.out
    assert "Events:" not in captured.out
    
    # Test events only
    args = argparse.Namespace(
        components=['QBtn'],
        sections=['events']
    )
    qinfo_command.execute(args)
    captured = capsys.readouterr()
    assert "Properties:" not in captured.out
    assert "Events:" in captured.out
    assert "click: Emitted when clicked" in captured.out


@patch('nicegui_atlas.commands.qinfo.get_cached_web_types')
def test_qinfo_command_multiple_components(mock_get_web_types, qinfo_command, capsys):
    """Test qinfo command with multiple components."""
    # Mock web-types data
    mock_get_web_types.return_value = {
        'contributions': {
            'html': {
                'tags': [
                    {
                        'name': 'QBtn',
                        'attributes': [{
                            'name': 'color',
                            'description': 'Color name for component',
                            'value': {'type': 'string'}
                        }]
                    },
                    {
                        'name': 'QInput',
                        'attributes': [{
                            'name': 'type',
                            'description': 'Input type',
                            'value': {'type': 'string'}
                        }]
                    }
                ]
            }
        }
    }
    
    # Execute command
    args = argparse.Namespace(
        components=['QBtn', 'QInput'],
        sections=None
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "=== QBtn ===" in captured.out
    assert "=== QInput ===" in captured.out
    assert "color (string): Color name for component" in captured.out
    assert "type (string): Input type" in captured.out


@patch('nicegui_atlas.commands.qinfo.get_cached_web_types')
def test_qinfo_command_component_not_found(mock_get_web_types, qinfo_command, capsys):
    """Test qinfo command with non-existent component."""
    # Mock web-types data
    mock_get_web_types.return_value = {
        'contributions': {
            'html': {
                'tags': []
            }
        }
    }
    
    # Execute command
    args = argparse.Namespace(
        components=['QNonExistent'],
        sections=None
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "Component QNonExistent not found" in captured.out


def test_get_component_info():
    """Test get_component_info function directly."""
    web_types = {
        'contributions': {
            'html': {
                'tags': [{
                    'name': 'QBtn',
                    'attributes': [{
                        'name': 'color',
                        'description': 'Color name for component',
                        'value': {'type': 'string'},
                        'doc-url': 'https://quasar.dev/vue-components/button'
                    }],
                    'events': [{
                        'name': 'click',
                        'description': 'Emitted when clicked',
                        'arguments': [{
                            'name': 'evt',
                            'type': 'Event',
                            'description': 'JS event object'
                        }]
                    }]
                }]
            }
        }
    }
    
    # Test with Q prefix
    info = get_component_info(web_types, 'QBtn')
    assert info['name'] == 'QBtn'
    assert info['doc_url'] == 'https://quasar.dev/vue-components/button'
    assert 'color' in info['properties']
    assert 'click' in info['events']
    
    # Test without Q prefix
    info = get_component_info(web_types, 'Btn')
    assert info['name'] == 'QBtn'
    
    # Test with sections filter
    info = get_component_info(web_types, 'QBtn', ['properties'])
    assert 'properties' in info
    assert 'events' in info  # Note: get_component_info always returns all sections
    
    # Test non-existent component
    info = get_component_info(web_types, 'QNonExistent')
    assert info is None
