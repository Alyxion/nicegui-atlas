# NiceGUI Atlas AI Rules

## Component Documentation

### Template Structure

The standard structure for component documentation is defined in `db/template.json`. This JSON Schema file specifies:
- Required and optional fields
- Field types and formats
- Field descriptions and constraints
- Nested structure requirements

When creating documentation for a new component:
1. Review the template at `db/template.json`
2. Ensure all required fields are included
3. Follow the specified formats and types
4. Validate against the schema

### Categories

Components are organized into the following categories:

1. Input Components (`db/input/`)
   - Form inputs, selectors, and controls

2. Basic Elements (`db/basic_elements/`)
   - Fundamental UI building blocks

3. Layout Components (`db/layout/`)
   - Structure and organization elements

### File Organization

- Component JSON files should be placed in the appropriate category directory under `db/`
- Filenames should match the component name in lowercase with underscores
- Each category has its own directory with a `categories.json` index

### Documentation Guidelines

1. Keep descriptions clear and concise
2. Include practical usage examples
3. Document all available props and events
4. Show common styling patterns
5. List typical use cases
6. Maintain consistent formatting

### Example Usage

```python
# Example of documenting a new component
{
  "name": "nicegui.ui.button",
  "source_path": "elements/button.py",
  "description": "Use to create clickable button elements.",
  "direct_ancestors": ["Element"],
  "quasar_components": ["QBtn"],
  "category": "Basic Elements",
  "python_props": {
    "__init__": {
      "text": {
        "type": "str",
        "description": "Button text",
        "default": "''"
      }
    }
  },
  "quasar_props": {
    "color": "Button color",
    "flat": "Flat style",
    "round": "Round shape"
  },
  "usage_examples": {
    "basic_button": {
      "description": "Simple button with click handler",
      "code": [
        "button = ui.button('Click me')",
        "def on_click():",
        "    print('Button clicked')",
        "button.on_click(on_click)"
      ]
    }
  },
  "common_use_cases": [
    "Form submission",
    "Action triggers",
    "Navigation"
  ],
  "styling": {
    "description": "Button styling options",
    "examples": {
      "classes": [
        "bg-primary",
        "text-white",
        "rounded-lg"
      ]
    }
  }
}
```

### Quasar Components

The Quasar component definitions are sourced from the web-types.json file, which provides comprehensive information about all available Quasar components, their properties, and documentation. The format of this file is documented in `docs/quasar_web_types_format.md`.

Key aspects of Quasar components:
1. All component names start with 'Q'
2. Properties are documented with types and descriptions
3. Documentation URLs are provided for each component
4. Default values are included where applicable

For detailed information about the web-types.json format and structure, refer to the format documentation.

### Validation

The cleanup script at `scripts/clean_component_jsons.py` enforces the template structure by:
1. Loading the template schema
2. Validating component JSONs
3. Removing non-standard fields
4. Ensuring required fields are present

Run the cleanup script after making changes to ensure consistency:
```bash
cd dependencies/nicegui-atlas
python scripts/clean_component_jsons.py
```
