import json
import os
from pathlib import Path
import requests
from typing import Dict, Any, List
import time

# Base URLs
QUASAR_DOCS_BASE = "https://quasar.dev/vue-components/"

def verify_url(url: str) -> bool:
    """Verify if a URL is accessible."""
    print(f"Verifying URL: {url}")
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            print(f"✓ URL is valid (Status: {response.status_code})")
            return True
        else:
            print(f"✗ URL returned status code: {response.status_code}")
            # Try GET request as fallback for endpoints that don't support HEAD
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ URL is valid via GET (Status: {response.status_code})")
                return True
            print(f"✗ URL is invalid via GET (Status: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"✗ Error verifying URL: {str(e)}")
        return False

def get_quasar_url(component_name: str) -> str:
    """Get the Quasar documentation URL for a component."""
    # Special cases for components with different URL patterns
    special_cases = {
        # Basic Elements
        'QBtn': 'button',
        'QBtnGroup': 'button-group',
        'QBtnDropdown': 'button-dropdown',
        'QBtnToggle': 'button-toggle',
        
        # Input Components
        'QOptionGroup': 'option-group',
        'QColor': 'color-picker',
        
        # Layout Components
        'QScrollArea': 'scroll-area',
        'QCardSection': 'card',  # Part of QCard docs
        'QCardActions': 'card',  # Part of QCard docs
        'QCarouselSlide': 'carousel',  # Part of QCarousel docs
        'QExpansionItem': 'expansion-item',
        'QLayout': 'layout',
        'QDrawer': 'drawer',
        'QPageContainer': 'layout',  # Part of QLayout docs
        'QPage': 'layout',  # Part of QLayout docs
        'QPageSticky': 'page-sticky',
        'QFooter': 'layout',  # Part of QLayout docs
        'QHeader': 'layout',  # Part of QLayout docs
        'QTabs': 'tabs',
        'QTab': 'tabs',  # Part of QTabs docs
        'QTabPanels': 'tab-panels',
        'QTabPanel': 'tab-panels',  # Part of QTabPanels docs
        'QStepper': 'stepper',
        'QStep': 'stepper',  # Part of QStepper docs
        'QStepperNavigation': 'stepper',  # Part of QStepper docs
    }
    
    # Check special cases first
    if component_name in special_cases:
        url = f"{QUASAR_DOCS_BASE}{special_cases[component_name]}"
    else:
        # Strip Q prefix and convert to lowercase
        name = component_name.lstrip('Q').lower()
        url = f"{QUASAR_DOCS_BASE}{name}"
    
    # Verify URL exists
    if verify_url(url):
        return url
    return ""

def update_component_urls(file_path: Path) -> None:
    """Update component URLs in a JSON file."""
    print(f"\nProcessing file: {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Skip if no Quasar components
    if 'quasar_components' not in data:
        print("No Quasar components found in file")
        return
    
    print("\nCurrent components:")
    print(json.dumps(data.get('quasar_components', []), indent=2))
    
    # Process components
    if not isinstance(data['quasar_components'], list):
        print("Invalid quasar_components format")
        return

    # Convert to list of objects if needed
    components = []
    for comp in data['quasar_components']:
        if isinstance(comp, str):
            components.append({"name": comp, "url": ""})
        elif isinstance(comp, dict) and "name" in comp:
            components.append(comp)
        else:
            print(f"Invalid component format: {comp}")
            continue

    # Update URLs for all components
    print("\nProcessing components:")
    data['quasar_components'] = []
    for comp in components:
        name = comp["name"]
        print(f"\nChecking component: {name}")
        url = get_quasar_url(name)
        if url:
            print(f"✓ Found URL for {name}: {url}")
            data['quasar_components'].append({
                "name": name,
                "url": url
            })
        else:
            print(f"✗ Could not verify URL for {name}")
            data['quasar_components'].append({
                "name": name,
                "url": ""
            })
        # Be nice to the server
        time.sleep(1)

    print("\nUpdated components:")
    print(json.dumps(data['quasar_components'], indent=2))
    
    # Write back the updated data
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def process_directory(dir_path: Path) -> None:
    """Process all JSON files in a directory."""
    for file_path in dir_path.glob('**/*.json'):
        if 'categories.json' in str(file_path) or 'template.json' in str(file_path):
            continue
        print(f'Processing {file_path}...')
        update_component_urls(file_path)

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
            process_directory(dir_path)

if __name__ == '__main__':
    main()
