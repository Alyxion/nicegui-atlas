"""Build command plugin for generating component overview in output directory."""

import argparse
import os
from typing import List
from .base import CommandPlugin, registry
from .index import IndexCommand


class BuildCommand(CommandPlugin):
    """Command for building component overview."""
    
    @property
    def name(self) -> str:
        return "build"
    
    @property
    def help(self) -> str:
        return "Build component overview in output directory"
    
    @property
    def examples(self) -> List[str]:
        return [
            "Build component overview:",
            "  python -m nicegui_atlas build"
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        # No additional arguments needed
        pass
    
    def execute(self, args: argparse.Namespace) -> None:
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create args for index command
        index_args = argparse.Namespace()
        index_args.output = os.path.join(output_dir, "component_overview.md")
        index_args.quiet = True
        
        # Use index command to generate documentation
        index_cmd = IndexCommand()
        index_cmd.execute(index_args)
        
        print(f"Component overview built in {index_args.output}")


# Register the plugin
registry.register(BuildCommand())
