import json
import os
from pathlib import Path
from typing import Dict, Any, Set

def load_template() -> Dict[str, Any]:
    """Load the template schema."""
    template_path = Path(__file__).parent.parent / 'db' / 'template.json'
    with open(template_path, 'r') as f:
        return json.load(f)

def get_allowed_fields(template: Dict[str, Any]) -> Set[str]:
    """Extract allowed field names from template."""
    return {k for k, v in template.items()}

def validate_required_fields(data: Dict[str, Any], template: Dict[str, Any]) -> None:
    """Ensure all required fields are present."""
    for field, schema in template.items():
        if schema.get('required', False) and field not in data:
            raise ValueError(f"Missing required field: {field}")

def clean_json_file(file_path: Path, template: Dict[str, Any], allowed_fields: Set[str]) -> None:
    """Clean a single JSON file using the template schema."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Keep only allowed fields
    cleaned_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    # Check for missing required fields
    missing_fields = []
    for field, schema in template.items():
        if schema.get('required', False) and field not in cleaned_data:
            missing_fields.append(field)
            # Add empty placeholder for required field
            if field == 'quasar_components':
                cleaned_data[field] = []
            elif field == 'direct_ancestors':
                cleaned_data[field] = []
            elif field == 'python_props':
                cleaned_data[field] = {"__init__": {}}
            elif field == 'quasar_props':
                cleaned_data[field] = {}
            elif field == 'usage_examples':
                cleaned_data[field] = {}
            elif field == 'common_use_cases':
                cleaned_data[field] = []
    
    if missing_fields:
        print(f"Warning: Added placeholders for missing required fields in {file_path}: {', '.join(missing_fields)}")
    
    # Write back the cleaned data
    with open(file_path, 'w') as f:
        json.dump(cleaned_data, f, indent=2)

def process_directory(dir_path: Path, template: Dict[str, Any], allowed_fields: Set[str]) -> None:
    """Process all JSON files in a directory."""
    for file_path in dir_path.glob('**/*.json'):
        if 'categories.json' in str(file_path) or 'template.json' in str(file_path):
            continue
        print(f'Processing {file_path}...')
        try:
            clean_json_file(file_path, template, allowed_fields)
        except ValueError as e:
            print(f"Error processing {file_path}: {e}")

def main():
    # Get the root directory of nicegui-atlas
    root_dir = Path(__file__).parent.parent
    
    # Load template and get allowed fields
    template = load_template()
    allowed_fields = get_allowed_fields(template)
    
    # Process input components
    input_dir = root_dir / 'db' / 'input'
    basic_elements_dir = root_dir / 'db' / 'basic_elements'
    layout_dir = root_dir / 'db' / 'layout'
    
    # Process each directory
    for dir_path in [input_dir, basic_elements_dir, layout_dir]:
        if dir_path.exists():
            process_directory(dir_path, template, allowed_fields)

if __name__ == '__main__':
    main()
