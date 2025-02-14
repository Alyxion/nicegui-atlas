# NiceGUI Atlas

A comprehensive documentation generator for NiceGUI UI components.

## Features

- Component information lookup with filtering
- Full component index generation
- Component overview builder
- Category-based organization with priorities
- Detailed technical information for each component

## Usage

Run `python -m nicegui_atlas --help` to see all available commands and options.

### Commands

- `info`: Show information about specific components
- `index`: Generate full component documentation
- `build`: Build component overview in output directory

### Examples

```bash
# Show info for a single component
python -m nicegui_atlas info ui.button

# Show info for multiple components with filtering
python -m nicegui_atlas info "ui.button;ui.checkbox" --filter "form,input"

# Build complete component overview
python -m nicegui_atlas build
```

The `build` command generates a comprehensive markdown file in the `output` directory, organizing components by category with detailed technical information and usage recommendations.
