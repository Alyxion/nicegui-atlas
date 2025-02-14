import json
import os
from pathlib import Path
from typing import Dict, Any

# Essential fields to keep
ALLOWED_FIELDS = {
    'name',
    'source_path',
    'description',
    'direct_ancestors',
    'quasar_components',
    'category',
    'component_file',
    'python_props',
    'events',
    'quasar_props',
    'usage_examples',
    'common_use_cases',
    'styling'
}

def clean_json_file(file_path: Path) -> None:
    """Remove extra fields from a JSON file."""
    print(f"\nProcessing file: {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Get current fields
    current_fields = set(data.keys())
    extra_fields = current_fields - ALLOWED_FIELDS
    if extra_fields:
        print(f"Removing extra fields: {', '.join(extra_fields)}")
        
        # Keep only allowed fields
        cleaned_data = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
        
        # Write back the cleaned data
        with open(file_path, 'w') as f:
            json.dump(cleaned_data, f, indent=2)
    else:
        print("No extra fields found")

def process_directory(dir_path: Path) -> None:
    """Process all JSON files in a directory."""
    for file_path in dir_path.glob('**/*.json'):
        if 'categories.json' in str(file_path) or 'template.json' in str(file_path):
            continue
        clean_json_file(file_path)

def main():
    # Get the root directory of nicegui-atlas
    root_dir = Path(__file__).parent.parent
    
    # Process input components
    input_dir = root_dir / 'db' / 'input'
    basic_elements_dir = root_dir / 'db' / 'basic_elements'
    layout_dir = root_dir / 'db' / 'layout'
    
    # Process each directory
    for dir_path in [input_dir, basic_elements_dir, layout_dir]:
        if dir_path.exists():
            print(f"\nProcessing directory: {dir_path}")
            process_directory(dir_path)

if __name__ == '__main__':
    main()
