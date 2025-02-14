"""Command-line interface for NiceGUI Atlas."""

import argparse
import sys
from .commands import registry


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='NiceGUI Atlas - Component Information and Documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\nExamples:\n" + "\n".join(registry.get_examples())
    )
    
    # Set up command parsers
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    registry.setup_parsers(subparsers)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command:
        plugin = registry.get_plugin(args.command)
        if plugin:
            plugin.execute(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
