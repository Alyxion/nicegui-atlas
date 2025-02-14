"""Info command plugin for displaying component information."""

import argparse
from typing import List
from .base import CommandPlugin, registry
from ..atlas import ComponentAtlas


class InfoCommand(CommandPlugin):
    """Command for displaying component information."""
    
    @property
    def name(self) -> str:
        return "info"
    
    @property
    def help(self) -> str:
        return "Show information about specific components"
    
    @property
    def examples(self) -> List[str]:
        return [
            "Show info for a single component:",
            "  python -m nicegui_atlas info ui.button",
            "",
            "Show info for multiple components:",
            "  python -m nicegui_atlas info \"ui.button;ui.checkbox;ui.card\"",
            "",
            "Show filtered components:",
            "  python -m nicegui_atlas info \"ui.button;ui.checkbox\" --filter \"form,input\""
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('components', help='Component names (semicolon-separated, e.g., "ui.button;ui.checkbox")')
        parser.add_argument('-f', '--filter', help='Filter components by terms (comma-separated)')
        parser.add_argument('-o', '--output', help='Output file path')
    
    def format_component(self, component):
        """Format a component for display."""
        tech_parts = []
        if component.direct_ancestors:
            tech_parts.append(f"Python: {', '.join(component.direct_ancestors)}")
        if component.quasar_components:
            if isinstance(component.quasar_components[0], dict):
                tech_parts.append(f"Quasar: {', '.join(c['name'] for c in component.quasar_components)}")
            else:
                tech_parts.append(f"Quasar: {', '.join(component.quasar_components)}")
        if component.libraries:
            tech_parts.append(f"Library: {', '.join(lib['name'] for lib in component.libraries)}")
        if component.internal_components:
            tech_parts.append(f"Internal: {', '.join(component.internal_components)}")
        if component.html_element:
            tech_parts.append(f"HTML: {component.html_element}")
        
        tech_info = ' | '.join(tech_parts)
        
        # Build the full line
        js_part = f" + {component.js_file}" if component.js_file else ""
        source = f"elements/{component.source_path.split('/')[-1]}"
        name = component.name.replace('nicegui.', '')  # Convert nicegui.ui.button to ui.button
        
        return f"`{name}` - [{source}{js_part}] ({tech_info}) {component.description}"
    
    def execute(self, args: argparse.Namespace) -> None:
        # Split components by semicolon and strip whitespace
        components = [c.strip() for c in args.components.split(';')]
        
        # Apply filter if provided
        if args.filter:
            filter_terms = [term.lower() for term in args.filter.split(',')]
            filtered_components = []
            for comp_name in components:
                component = ComponentAtlas.get_component(comp_name)
                if component:
                    # Check if any filter term is in name, description, or tech info
                    component_text = (
                        f"{component.name} {component.description} "
                        f"{' '.join(component.direct_ancestors or [])} "
                        f"{' '.join(str(c) for c in (component.quasar_components or []))} "
                        f"{' '.join(lib['name'] for lib in (component.libraries or []))}"
                    ).lower()
                    if any(term in component_text for term in filter_terms):
                        filtered_components.append(component)
            components_to_show = filtered_components
        else:
            components_to_show = [ComponentAtlas.get_component(name) for name in components]
            components_to_show = [c for c in components_to_show if c]  # Remove None values
        
        if not components_to_show:
            print("No components found matching the criteria.")
            return
        
        # Format each component and join with newlines
        lines = [f"- {self.format_component(component)}" for component in components_to_show]
        output = '\n'.join(lines)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output + '\n')
            print(f"Output written to {args.output}")
        else:
            print(output)


# Register the plugin
registry.register(InfoCommand())
