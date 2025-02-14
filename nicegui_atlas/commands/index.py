"""Index command plugin for generating full component documentation."""

import argparse
from typing import List
from .base import CommandPlugin, registry
from ..atlas import ComponentAtlas


class IndexCommand(CommandPlugin):
    """Command for generating full component documentation."""
    
    @property
    def name(self) -> str:
        return "index"
    
    @property
    def help(self) -> str:
        return "Generate full component documentation"
    
    @property
    def examples(self) -> List[str]:
        return [
            "Generate full index:",
            "  python -m nicegui_atlas index",
            "",
            "Generate index to file without console output:",
            "  python -m nicegui_atlas index -o docs/components.md --quiet"
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-o', '--output', help='Output file path')
        parser.add_argument('-q', '--quiet', action='store_true', help='Suppress console output')
    
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
        content = ["# NiceGUI UI Components\n",
                  "A comprehensive list of all available NiceGUI UI components with implementation details and usage recommendations.\n"]
        
        # Get categories sorted by priority
        categories = ComponentAtlas.get_categories()
        
        for category in categories:
            content.append(f"## {category.name}\n")
            if category.description:
                content.append(f"{category.description}\n")
            
            components = ComponentAtlas.get_category(category.id)
            if components:
                # Sort components by name within each category
                sorted_components = sorted(components, key=lambda x: str(x.name))
                # Add components
                for component in sorted_components:
                    content.append(f"- {self.format_component(component)}")
                # Add blank line after category
                content.append("")
        
        output = '\n'.join(content)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output + '\n')
            print(f"Generated documentation in {args.output}")
        
        if not args.quiet:
            print(output)


# Register the plugin
registry.register(IndexCommand())
