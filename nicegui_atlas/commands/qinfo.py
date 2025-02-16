"""Command for fetching Quasar component information."""

import argparse
import json
from typing import List, Optional

from .base import CommandPlugin, registry as command_registry
from ..registry import registry


def format_component_info(component: 'ComponentInfo', sections: Optional[List[str]] = None) -> str:
    """Format component information for display.
    
    Args:
        component: The component information
        sections: Optional list of sections to include ('properties', 'events')
                 If None, includes all sections
    
    Returns:
        Formatted string with component information
    """
    lines = [f"\n=== {component.name} ==="]
    
    if component.doc_url:
        lines.append(f"Documentation: {component.doc_url}\n")
    
    if not sections or 'properties' in sections:
        if component.properties:
            lines.append("Properties:")
            for name, prop in component.properties.items():
                desc = prop.description or ""
                if desc:
                    # Truncate description if too long
                    if len(desc) > 60:
                        desc = desc.split(';')[0].strip()
                    desc = f": {desc}"
                lines.append(f"  {name} ({prop.type}){desc}")
            lines.append("")
    
    if not sections or 'events' in sections:
        if component.events:
            lines.append("Events:")
            for name, event in component.events.items():
                desc = event.description or ""
                if desc:
                    if len(desc) > 60:
                        desc = desc.split(';')[0].strip()
                    desc = f": {desc}"
                lines.append(f"  {name}{desc}")
                if event.arguments:
                    lines.append("    Arguments:")
                    for arg in event.arguments:
                        arg_desc = arg.description or ""
                        if arg_desc and len(arg_desc) > 60:
                            arg_desc = arg_desc.split(';')[0].strip()
                        lines.append(f"      {arg.name} ({arg.type}): {arg_desc}")
            lines.append("")
    
    return "\n".join(lines)


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
            "nicegui-atlas qinfo QInput --sections events",
            "nicegui-atlas qinfo QBtn --raw"
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
        parser.add_argument(
            '-r', '--raw',
            action='store_true',
            default=False,
            help='Output raw JSON instead of formatted text'
        )
    
    def execute(self, args: argparse.Namespace) -> None:
        components = []
        for component_name in args.components:
            component = registry.get_quasar_component(component_name)
            if component:
                components.append(component)
            else:
                print(f"\nComponent {component_name} not found.")
        
        if not components:
            return

        if args.raw:
            # Output raw JSON
            print(json.dumps([comp.dict() for comp in components], indent=2))
        else:
            # Output formatted text
            for component in components:
                print(format_component_info(component, args.sections))


# Register the command
command_registry.register(QInfoCommand())
