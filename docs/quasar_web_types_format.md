# Quasar Web Types Format

This document describes the format of the Quasar web-types.json file used for component verification and documentation.

## File Structure

```json
{
  "$schema": "",
  "framework": "vue",
  "name": "quasar",
  "version": "2.16.9",
  "contributions": {
    "html": {
      "types-syntax": "typescript",
      "tags": [
        {
          "name": "QComponentName",
          "source": {
            "module": "quasar",
            "symbol": "QComponentName"
          },
          "attributes": [
            {
              "name": "property-name",
              "value": {
                "kind": "expression",
                "type": "property-type"
              },
              "description": "Property description",
              "doc-url": "https://v2.quasar.dev/vue-components/component-name",
              "default": "default-value"
            }
          ]
        }
      ]
    }
  }
}
```

## Key Sections

### Top Level
- `$schema`: Schema definition (usually empty)
- `framework`: Always "vue" for Quasar
- `name`: Always "quasar"
- `version`: Quasar version number
- `contributions`: Contains all component definitions

### HTML Contributions
Located under `contributions.html`:
- `types-syntax`: Usually "typescript"
- `tags`: Array of component definitions

### Component Definition
Each component in the `tags` array has:
- `name`: Component name (e.g., "QButton")
- `source`: Component source information
  - `module`: Usually "quasar"
  - `symbol`: Same as component name

### Property Definition
Each property in a component's `attributes` array has:
- `name`: Property name
- `value`: Type information
  - `kind`: Usually "expression"
  - `type`: TypeScript type definition
- `description`: Property description
- `doc-url`: Link to component documentation
- `default`: Default value if any

## Example Component Entry

```json
{
  "name": "QBtn",
  "source": {
    "module": "quasar",
    "symbol": "QBtn"
  },
  "attributes": [
    {
      "name": "size",
      "value": {
        "kind": "expression",
        "type": "string"
      },
      "description": "Size in CSS units including unit name or standard size name (xs|sm|md|lg|xl)",
      "doc-url": "https://v2.quasar.dev/vue-components/button",
      "default": "md"
    }
  ]
}
```

## Usage Notes

1. Component names always start with 'Q'
2. Properties use kebab-case in the JSON
3. Documentation URLs follow the pattern: https://v2.quasar.dev/vue-components/[component-name]
4. Type definitions use TypeScript syntax
5. Default values are provided as strings, even for numbers and booleans
