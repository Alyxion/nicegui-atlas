"""Verify command plugin for checking component properties against Quasar documentation."""

import argparse
import os
from typing import List
from .base import CommandPlugin, registry
from ..quasar_verifier import verify_components
from ..component_finder import ComponentFinder


class VerifyCommand(CommandPlugin):
    """Command for verifying component properties."""
    
    @property
    def name(self) -> str:
        return "verify"
    
    @property
    def help(self) -> str:
        return "Verify component properties against Quasar documentation"
    
    @property
    def examples(self) -> List[str]:
        return [
            "Verify a specific component:",
            "  python -m nicegui_atlas verify ui.button",
            "",
            "Verify components by filter:",
            "  python -m nicegui_atlas verify --filter basic/*",
            "  python -m nicegui_atlas verify --filter input/*",
            "",
            "Verify all components:",
            "  python -m nicegui_atlas verify --all",
            "",
            "Verify with specific versions:",
            "  python -m nicegui_atlas verify ui.button --quasar-version 2.16.9 --vue-version 3.4.38"
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        group = parser.add_mutually_exclusive_group()
        group.add_argument('component', nargs='?', help='Component name (e.g., "ui.button")')
        group.add_argument('--filter', help='Filter pattern (e.g., "basic/*", "input/*")')
        group.add_argument('--all', action='store_true', help='Verify all components')
        parser.add_argument('--quasar-version', default='2.16.9', help='Quasar version to verify against')
        parser.add_argument('--vue-version', default='3.4.38', help='Vue version to verify against')
        parser.add_argument('-o', '--output', help='Output file for detailed report')
    
    def execute(self, args: argparse.Namespace) -> None:
        finder = ComponentFinder()
        
        # Get component paths based on input
        if args.component:
            paths = finder.find_by_name(args.component)
            if not paths:
                print(f"No component files found matching '{args.component}'")
                return
        elif args.filter:
            paths = finder.find_by_filter(args.filter)
            if not paths:
                print(f"No component files found matching filter '{args.filter}'")
                return
        elif args.all:
            paths = finder.find_all()
            if not paths:
                print("No component files found")
                return
        else:
            print("Please specify a component name, filter pattern, or use --all")
            return
        
        # Verify components
        results = verify_components(
            paths,
            quasar_version=args.quasar_version,
            vue_version=args.vue_version
        )
        
        # Print summary
        total_issues = sum(len(issues) for issues in results.values())
        if total_issues == 0:
            print("\nAll components verified successfully!")
        else:
            print(f"\nFound {total_issues} issues across {len(results)} components:")
            for path, issues in results.items():
                if issues:
                    print(f"\n{os.path.basename(path)}:")
                    for issue in issues:
                        print(f"  - {issue}")
            
            if args.output:
                # Write detailed report to file
                with open(args.output, 'w') as f:
                    f.write("# Component Verification Report\n\n")
                    for path, issues in results.items():
                        if issues:
                            f.write(f"\n## {os.path.basename(path)}\n")
                            for issue in issues:
                                f.write(f"- {issue}\n")
                print(f"\nDetailed report written to {args.output}")


# Register the plugin
registry.register(VerifyCommand())
