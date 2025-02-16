# NiceGUI Atlas

A comprehensive documentation generator for NiceGUI UI components.

## Features

- Component information lookup with filtering
- Full component index generation
- Component overview builder
- Category-based organization with priorities
- Detailed technical information for each component
- Component file backup with change tracking

## Usage

Run `python -m nicegui_atlas --help` to see all available commands and options.

### Commands

- `info`: Show information about specific components
- `index`: Generate full component documentation
- `build`: Build component overview in output directory
- `backup`: ckCreate backups of component files with checksums

### Examples

```bash
# Show info for a single component
python -m nicegui_atlas info ui.button

# Show info for multiple components with filtering
python -m nicegui_atlas info "ui.button;ui.checkbox" --filter "form,input"

# Build complete component overview
python -m nicegui_atlas build

# Create backups of all component files
python -m nicegui_atlas backup

# Clean old backups and create new ones
python -m nicegui_atlas backup --clean

# Specify custom backup directory
python -m nicegui_atlas backup --output-dir path/to/dir
```

The `build` command generates a comprehensive markdown file in the `output` directory, organizing components by category with detailed technical information and usage recommendations.

The `backup` command creates backups of all component files referenced in JSON files:
- Backs up Python source files and associated JavaScript files
- Maintains library files for components that use them
- Adds MD5 checksums to JSON files for tracking changes
- Can be used programmatically in addition to CLI usage
