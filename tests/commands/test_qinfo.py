"""Tests for the qinfo command plugin."""

import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from nicegui_atlas.commands.qinfo import QInfoCommand


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
    assert not args.raw
    
    args = parser.parse_args(['QBtn', '--sections', 'properties', 'events', '--raw'])
    assert args.components == ['QBtn']
    assert args.sections == ['properties', 'events']
    assert args.raw


@patch('nicegui_atlas.commands.qinfo.registry')
def test_qinfo_command_single_component(mock_registry, qinfo_command, capsys):
    """Test qinfo command with a single component."""
    from nicegui_atlas.models import ComponentInfo, PropertyInfo, EventInfo, ArgumentInfo
    
    # Mock component data
    mock_component = ComponentInfo(
        name="QBtn",
        type="quasar",
        description="Button component",
        doc_url="https://quasar.dev/vue-components/button",
        properties={
            "color": PropertyInfo(
                name="color",
                type="string",
                description="Color name for component"
            )
        },
        events={
            "click": EventInfo(
                name="click",
                description="Emitted when clicked",
                arguments=[
                    ArgumentInfo(
                        name="evt",
                        type="Event",
                        description="JS event object"
                    )
                ]
            )
        }
    )
    mock_registry.get_quasar_component.return_value = mock_component
    
    # Execute command
    args = argparse.Namespace(
        components=['QBtn'],
        sections=None,
        raw=False
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "=== QBtn ===" in captured.out
    assert "Documentation: https://quasar.dev/vue-components/button" in captured.out
    assert "color (string): Color name for component" in captured.out
    assert "click: Emitted when clicked" in captured.out
    assert "evt (Event): JS event object" in captured.out


@patch('nicegui_atlas.commands.qinfo.registry')
def test_qinfo_command_without_q_prefix(mock_registry, qinfo_command, capsys):
    """Test qinfo command with component name without Q prefix."""
    from nicegui_atlas.models import ComponentInfo, PropertyInfo
    
    # Mock component data
    mock_component = ComponentInfo(
        name="QBtn",
        type="quasar",
        properties={
            "color": PropertyInfo(
                name="color",
                type="string",
                description="Color name for component"
            )
        }
    )
    mock_registry.get_quasar_component.return_value = mock_component
    
    # Execute command
    args = argparse.Namespace(
        components=['Btn'],
        sections=None,
        raw=False
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "=== QBtn ===" in captured.out
    assert "color (string): Color name for component" in captured.out


@patch('nicegui_atlas.commands.qinfo.registry')
def test_qinfo_command_with_sections(mock_registry, qinfo_command, capsys):
    """Test qinfo command with specific sections."""
    from nicegui_atlas.models import ComponentInfo, PropertyInfo, EventInfo
    
    # Mock component data
    mock_component = ComponentInfo(
        name="QBtn",
        type="quasar",
        properties={
            "color": PropertyInfo(
                name="color",
                type="string",
                description="Color name for component"
            )
        },
        events={
            "click": EventInfo(
                name="click",
                description="Emitted when clicked"
            )
        }
    )
    mock_registry.get_quasar_component.return_value = mock_component
    
    # Test properties only
    args = argparse.Namespace(
        components=['QBtn'],
        sections=['properties'],
        raw=False
    )
    qinfo_command.execute(args)
    captured = capsys.readouterr()
    assert "Properties:" in captured.out
    assert "color (string): Color name for component" in captured.out
    assert "Events:" not in captured.out
    
    # Test events only
    args = argparse.Namespace(
        components=['QBtn'],
        sections=['events'],
        raw=False
    )
    qinfo_command.execute(args)
    captured = capsys.readouterr()
    assert "Properties:" not in captured.out
    assert "Events:" in captured.out
    assert "click: Emitted when clicked" in captured.out


@patch('nicegui_atlas.commands.qinfo.registry')
def test_qinfo_command_multiple_components(mock_registry, qinfo_command, capsys):
    """Test qinfo command with multiple components."""
    from nicegui_atlas.models import ComponentInfo, PropertyInfo
    
    # Mock component data
    mock_btn = ComponentInfo(
        name="QBtn",
        type="quasar",
        properties={
            "color": PropertyInfo(
                name="color",
                type="string",
                description="Color name for component"
            )
        }
    )
    mock_input = ComponentInfo(
        name="QInput",
        type="quasar",
        properties={
            "type": PropertyInfo(
                name="type",
                type="string",
                description="Input type"
            )
        }
    )
    
    def get_component(name):
        if name in ["QBtn", "Btn"]:
            return mock_btn
        elif name in ["QInput", "Input"]:
            return mock_input
        return None
    
    mock_registry.get_quasar_component.side_effect = get_component
    
    # Execute command
    args = argparse.Namespace(
        components=['QBtn', 'QInput'],
        sections=None,
        raw=False
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "=== QBtn ===" in captured.out
    assert "=== QInput ===" in captured.out
    assert "color (string): Color name for component" in captured.out
    assert "type (string): Input type" in captured.out


@patch('nicegui_atlas.commands.qinfo.registry')
def test_qinfo_command_component_not_found(mock_registry, qinfo_command, capsys):
    """Test qinfo command with non-existent component."""
    mock_registry.get_quasar_component.return_value = None
    
    # Execute command
    args = argparse.Namespace(
        components=['QNonExistent'],
        sections=None,
        raw=False
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    assert "Component QNonExistent not found" in captured.out


@patch('nicegui_atlas.commands.qinfo.registry')
def test_qinfo_command_raw_output(mock_registry, qinfo_command, capsys):
    """Test qinfo command with raw JSON output."""
    from nicegui_atlas.models import ComponentInfo, PropertyInfo, EventInfo
    
    # Mock component data
    mock_component = ComponentInfo(
        name="QBtn",
        type="quasar",
        description="Button component",
        doc_url="https://quasar.dev/vue-components/button",
        properties={
            "color": PropertyInfo(
                name="color",
                type="string",
                description="Color name for component"
            )
        },
        events={
            "click": EventInfo(
                name="click",
                description="Emitted when clicked"
            )
        }
    )
    mock_registry.get_quasar_component.return_value = mock_component
    
    # Execute command
    args = argparse.Namespace(
        components=['QBtn'],
        sections=None,
        raw=True
    )
    qinfo_command.execute(args)
    
    # Check output
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert isinstance(output, list)
    assert len(output) == 1
    assert output[0]["name"] == "QBtn"
    assert output[0]["type"] == "quasar"
    assert output[0]["description"] == "Button component"
    assert output[0]["doc_url"] == "https://quasar.dev/vue-components/button"
    assert "color" in output[0]["properties"]
    assert "click" in output[0]["events"]
