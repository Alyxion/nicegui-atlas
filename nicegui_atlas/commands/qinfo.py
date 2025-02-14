"""Command for fetching Quasar component information."""

import argparse
from typing import List, Optional

from .base import CommandPlugin, registry
from ..quasar_verifier import get_cached_web_types


class QInfoCommand(CommandPlugin):
    """Command plugin for getting Quasar component information."""
    
    @property
    def name(self) -> str:
        return "qinfo"
    
    @property
    def help(self) -> str:
        return "Get information about Quasar components"
    
    @property
    def examples(self) -> List[str]:
        return [
            "nicegui-atlas qinfo QBtn",
            "nicegui-atlas qinfo QTable QSelect --sections properties",
            "nicegui-atlas qinfo QInput --sections events"
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'components',
            nargs='+',
            help='Names of components to get info for (with or without Q prefix)'
        )
        parser.add_argument(
            '--sections',
            nargs='+',
            choices=['properties', 'events'],
            help='Specific sections to include (default: all)'
        )
    
    def execute(self, args: argparse.Namespace) -> None:
        web_types = get_cached_web_types()
        
        for component in args.components:
            info = get_component_info(web_types, component, args.sections)
            if info:
                print(f"\n=== {info['name']} ===")
                if info['doc_url']:
                    print(f"Documentation: {info['doc_url']}\n")
                
                if 'properties' in info and (not args.sections or 'properties' in args.sections):
                    print("Properties:")
                    for name, prop in info['properties'].items():
                        desc = prop['description'].split('\n')[0].split('Examples:')[0].strip()
                        # Truncate description if too long
                        if len(desc) > 60:
                            desc = desc.split(';')[0].strip()
                        print(f"  {name} ({prop['type']}): {desc}")
                    print()
                
                if 'events' in info and (not args.sections or 'events' in args.sections):
                    print("Events:")
                    for name, event in info['events'].items():
                        desc = event['description'].split('\n')[0].split('Examples:')[0].strip()
                        if len(desc) > 60:
                            desc = desc.split(';')[0].strip()
                        print(f"  {name}: {desc}")
                        if event['args']:
                            print("    Arguments:")
                            for arg in event['args']:
                                arg_desc = arg['description'].split('\n')[0].split('Examples:')[0].strip()
                                if len(arg_desc) > 60:
                                    arg_desc = arg_desc.split(';')[0].strip()
                                print(f"      {arg['name']} ({arg['type']}): {arg_desc}")
                    print()
            else:
                print(f"\nComponent {component} not found.")


def get_component_info(web_types: dict, component_name: str, 
                      sections: Optional[List[str]] = None) -> dict:
    """Get information about a specific component.
    
    Args:
        web_types: The web-types.json data
        component_name: Name of the component (with or without Q prefix)
        sections: Optional list of sections to include ('properties', 'events', etc.)
                 If None, includes all sections
    
    Returns:
        Dictionary containing the requested component information
    """
    # Ensure component name starts with Q
    if not component_name.startswith('Q'):
        component_name = 'Q' + component_name

    # Find the component in web-types
    for tag in web_types.get('contributions', {}).get('html', {}).get('tags', []):
        if tag.get('name') == component_name:
            result = {
                'name': component_name,
                'doc_url': None,
                'properties': {},
                'events': {},
            }
            
            # Extract properties if requested or if no sections specified
            if not sections or 'properties' in sections:
                for attr in tag.get('attributes', []):
                    name = attr.get('name', '')
                    if name:
                        value_info = attr.get('value', {})
                        result['properties'][name] = {
                            'type': value_info.get('type', ''),
                            'kind': value_info.get('kind', ''),
                            'description': attr.get('description', ''),
                            'default': attr.get('default', None),
                            'required': attr.get('required', False),
                            'doc_url': attr.get('doc-url', None)
                        }
                        # Get doc_url from first property that has it
                        if not result['doc_url'] and 'doc-url' in attr:
                            result['doc_url'] = attr['doc-url']
            
            # Extract events if requested or if no sections specified
            if not sections or 'events' in sections:
                for event in tag.get('events', []):
                    name = event.get('name', '')
                    if name:
                        result['events'][name] = {
                            'description': event.get('description', ''),
                            'args': event.get('arguments', [])
                        }
            
            return result
    
    return None

# Register the command
registry.register(QInfoCommand())
