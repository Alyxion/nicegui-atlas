#!/usr/bin/env python3
"""Script to scan all component JSON files for event types."""

import json
import os
from typing import Set


def scan_file_for_event_types(file_path: str) -> Set[str]:
    """Scan a single JSON file for event types."""
    event_types = set()
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            # Check python_props for event handler types
            if 'python_props' in data:
                for prop in data['python_props'].get('__init__', {}).values():
                    if isinstance(prop, dict) and 'type' in prop:
                        type_str = prop['type']
                        if 'EventArguments' in type_str:
                            # Extract event type from Handler[EventType] format
                            if '[' in type_str and ']' in type_str:
                                event_type = type_str.split('[')[1].split(']')[0]
                                event_types.add(event_type)
            
            # Check events section
            if 'events' in data:
                for event in data['events'].values():
                    if isinstance(event, dict) and 'arguments' in event:
                        if isinstance(event['arguments'], str) and 'EventArguments' in event['arguments']:
                            # Extract event type from constructor call format
                            event_type = event['arguments'].split('(')[0]
                            event_types.add(event_type)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return event_types


def main():
    """Scan all component JSON files for event types."""
    db_dir = 'db'
    event_types = set()
    
    # Walk through all directories in db
    for root, _, files in os.walk(db_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                event_types.update(scan_file_for_event_types(file_path))
    
    print("\nFound event types:")
    for event_type in sorted(event_types):
        print(f"- {event_type}")


if __name__ == '__main__':
    main()
