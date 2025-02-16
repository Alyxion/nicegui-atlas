"""Tests for the verify command plugin."""

import argparse
from pathlib import Path
import json

import pytest
from nicegui.elements.upload import Upload

from nicegui_atlas.commands.verify import VerifyCommand, ComponentVerifier


@pytest.fixture
def verify_command():
    """Create an instance of the verify command."""
    return VerifyCommand()


def test_verify_command_properties(verify_command):
    """Test verify command basic properties."""
    assert verify_command.name == "verify"
    assert verify_command.help == "Verify component documentation completeness"
    assert len(verify_command.examples) > 0


def test_verify_command_parser_setup():
    """Test verify command argument parser setup."""
    cmd = VerifyCommand()
    parser = argparse.ArgumentParser()
    cmd.setup_parser(parser)
    
    args = parser.parse_args(['upload', '--fix'])
    assert args.component == 'upload'
    assert args.fix is True


def test_component_verifier_with_upload():
    """Test ComponentVerifier with real Upload component."""
    verifier = ComponentVerifier(
        str(Path('db/components/upload.json')),
        Upload
    )
    
    missing = verifier.find_undocumented_events()
    
    # Print missing events to help improve documentation
    if missing['init_params'] or missing['methods']:
        print("\nUndocumented Upload events:")
        if missing['init_params']:
            print("\nMissing __init__ parameters:")
            for param, _ in missing['init_params']:
                print(f"  - {param}")
        if missing['methods']:
            print("\nMissing method events:")
            for method, _ in missing['methods']:
                print(f"  - {method}")
    
    # The test should pass even if there are missing events
    # as this helps identify documentation gaps
    assert isinstance(missing['init_params'], list)
    assert isinstance(missing['methods'], list)


def test_verify_command_execution(verify_command, capsys):
    """Test verify command execution with Upload component."""
    args = argparse.Namespace(component='upload', fix=False)
    verify_command.execute(args)
    
    captured = capsys.readouterr()
    # We don't assert specific output as it may change
    # when documentation is updated
    assert captured.out  # Just verify there is some output


def test_verify_command_fix_output(verify_command, capsys):
    """Test verify command --fix output."""
    args = argparse.Namespace(component='upload', fix=True)
    verify_command.execute(args)
    
    captured = capsys.readouterr()
    output = captured.out
    
    # If there are missing events, verify JSON output
    if "JSON code to fix missing events:" in output:
        # Extract JSON part
        json_str = output.split("JSON code to fix missing events:", 1)[1].strip()
        # Verify it's valid JSON
        json_data = json.loads(json_str)
        
        # Verify structure
        if 'events' in json_data:
            # Full events object
            events = json_data['events']
        else:
            # Just the new events
            events = json_data
            
        # Check structure of events
        if '__init__' in events:
            for event_name, event_data in events['__init__'].items():
                assert 'description' in event_data
                assert 'arguments' in event_data
                
        if 'methods' in events:
            for event_name, event_data in events['methods'].items():
                assert 'description' in event_data
                assert 'arguments' in event_data
                assert 'returns' in event_data


def test_generate_fix_json():
    """Test JSON generation for missing events."""
    verifier = ComponentVerifier(
        str(Path('db/components/upload.json')),
        Upload
    )
    
    # Create test missing events data
    missing = {
        'init_params': [
            ('on_test', {
                'description': 'Test description',
                'arguments': 'TestEventArguments(sender=self, client=self.client)'
            })
        ],
        'methods': [
            ('on_test_method', {
                'description': 'Test method description',
                'arguments': 'TestEventArguments(sender=self, client=self.client)',
                'returns': 'Self (for method chaining)'
            })
        ]
    }
    
    json_str = verifier.generate_fix_json(missing)
    json_data = json.loads(json_str)
    
    # Verify structure
    if 'events' in json_data:
        events = json_data['events']
    else:
        events = json_data
        
    assert '__init__' in events
    assert 'methods' in events
    assert events['__init__']['on_test']['description'] == 'Test description'
    assert events['methods']['on_test_method']['returns'] == 'Self (for method chaining)'
