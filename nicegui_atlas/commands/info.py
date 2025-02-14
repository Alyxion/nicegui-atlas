"""Info command plugin for displaying component information."""

import argparse
from typing import List, Optional

from .base import CommandPlugin, registry as command_registry
from ..registry import registry
from ..formatters import format_component
from ..models import ComponentInfo


class InfoCommand(CommandPlugin):
    """Command for displaying component information."""
    
    @property
    def name(self) -> str:
        return "info"
    
    @property
    def help(self) -> str:
        return "Show information about NiceGUI or Quasar components"
    
    @property
    def examples(self) -> List[str]:
        return [
            "Show info for a NiceGUI component:",
            "  python -m nicegui_atlas info ui.button",
            "",
            "Show info for a Quasar component:",
            "  python -m nicegui_atlas info --quasar QBtn",
            "",
            "Show info for multiple NiceGUI components:",
            "  python -m nicegui_atlas info \"ui.button;ui.checkbox;ui.card\"",
            "",
            "Show filtered sections:",
            "  python -m nicegui_atlas info ui.button --sections properties,events",
            "",
            "Show filtered components:",
            "  python -m nicegui_atlas info \"ui.button;ui.checkbox\" --filter \"form,input\""
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('components', help='Component names (semicolon-separated, e.g., "ui.button;ui.checkbox")')
        parser.add_argument('-q', '--quasar', action='store_true', help='Show Quasar component info')
        parser.add_argument('-s', '--sections', help='Sections to show (comma-separated: properties,events,functions)')
        parser.add_argument('-f', '--filter', help='Filter components by terms (comma-separated)')
        parser.add_argument('-o', '--output', help='Output file path')
    
    def get_component(self, name: str, is_quasar: bool = False) -> Optional[ComponentInfo]:
        """Get a component by name."""
        if is_quasar:
            return registry.get_quasar_component(name)
        else:
            # Add nicegui prefix if not present
            full_name = name if name.startswith('nicegui.') else f'nicegui.{name}'
            return registry.get_nicegui_component(full_name)
    
    def execute(self, args: argparse.Namespace) -> None:
        # Split components by semicolon and strip whitespace
        components = [c.strip() for c in args.components.split(';')]
        
        # Parse sections if provided
        sections = None
        if args.sections:
            sections = [s.strip() for s in args.sections.split(',')]
        
        # Apply filter if provided
        if args.filter:
            filter_terms = [term.lower() for term in args.filter.split(',')]
            filtered_components = []
            for comp_name in components:
                component = self.get_component(comp_name, args.quasar)
                if component:
                    # Check if any filter term is in component text
                    component_text = (
                        f"{component.name} {component.description} "
                        f"{' '.join(component.direct_ancestors or [])} "
                        f"{' '.join(str(c) for c in (component.quasar_components or []))}"
                    ).lower()
                    if any(term in component_text for term in filter_terms):
                        filtered_components.append(component)
            components_to_show = filtered_components
        else:
            components_to_show = [
                self.get_component(name, args.quasar)
                for name in components
            ]
            components_to_show = [c for c in components_to_show if c]  # Remove None values
        
        if not components_to_show:
            print("No components found matching the criteria.")
            return
        
        # Format each component
        output = ""
        for component in components_to_show:
            output += format_component(component, sections)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output.strip() + '\n')
            print(f"Output written to {args.output}")
        else:
            print(output.strip())


# Register the plugin
command_registry.register(InfoCommand())
