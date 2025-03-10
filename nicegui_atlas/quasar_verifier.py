"""Quasar component verifier using web-types."""

import json
import os
from pathlib import Path
from typing import Dict, Set, Tuple
from packaging import version

CONFIG_FILE = Path(__file__).parent / "config.json"
WEB_TYPES_FILE = Path(__file__).parent.parent / "db" / "quasar-web-types.json"

def load_config() -> dict:
    """Load configuration from JSON file."""
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_web_types() -> dict:
    """Get web-types.json from the repository."""
    try:
        with open(WEB_TYPES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load web-types.json: {str(e)}")

def load_component_mappings() -> tuple[dict, dict]:
    """Load component mappings from JSON file."""
    mappings_file = Path(__file__).parent.parent / "db" / "component_mappings.json"
    with open(mappings_file, 'r') as f:
        data = json.load(f)
    return data["url_mappings"], data["shared_pages"]

def get_quasar_url(comp_name: str) -> str:
    """Get the Quasar documentation URL for a component."""
    # Convert component name to lowercase and remove 'q' prefix
    name = comp_name.lower().replace('q', '', 1)
    
    # Load mappings from JSON file
    url_mappings, _ = load_component_mappings()
    
    # Map component name if it exists in special cases
    name = url_mappings.get(name, name)
    
    # Special case for plugins
    if name == "notify":
        return f"https://quasar.dev/quasar-plugins/{name}"
    
    # Special case for table components
    if name in ["table-row", "table-header", "table-cell"]:
        return "https://quasar.dev/vue-components/table"
    
    # Use vue-components path for all components
    url = f"https://quasar.dev/vue-components/{name}"
    
    # Remove trailing slash if present
    return url.rstrip('/')

def extract_quasar_props(comp_name: str, web_types: dict) -> Dict[str, str]:
    """Extract properties from web-types.json for a component."""
    props = {}
    
    # Remove 'Q' prefix if present for matching
    search_name = comp_name.replace('Q', '', 1) if comp_name.startswith('Q') else comp_name
    
    # Find the component in web-types
    types = web_types.get('contributions', {}).get('html', {}).get('types-syntax', [])
    for type_def in types:
        if type_def.get('source', {}).get('module') == 'quasar' and type_def.get('symbol', '').lower() == search_name.lower():
            # Found the component, now get its properties
            for prop in type_def.get('properties', []):
                prop_name = prop.get('name', '')
                prop_desc = prop.get('description', '')
                if prop_name:
                    props[prop_name] = prop_desc
    
    # Also check tags for additional properties
    for tag in web_types.get('contributions', {}).get('html', {}).get('tags', []):
        if tag.get('name', '').lower() == f"q-{search_name.lower()}":
            for attr in tag.get('attributes', []):
                prop_name = attr.get('name', '')
                prop_desc = attr.get('description', '')
                if prop_name:
                    props[prop_name] = prop_desc
    
    return props

def compare_props(quasar_props: Dict[str, str], our_props: Dict[str, str]) -> Tuple[Set[str], Set[str]]:
    """Compare Quasar properties with our properties.
    
    Returns:
        Tuple of (missing_props, extra_props)
    """
    quasar_prop_names = set(quasar_props.keys())
    our_prop_names = set(our_props.keys())
    
    # Debug output
    print("\nComparing properties:")
    print(f"Quasar props: {sorted(quasar_prop_names)}")
    print(f"Our props: {sorted(our_prop_names)}")
    
    missing_props = quasar_prop_names - our_prop_names
    extra_props = our_prop_names - quasar_prop_names
    
    return missing_props, extra_props

def verify_component(comp_name: str, comp_url: str, component_data: dict, web_types: dict) -> list[str]:
    """Verify a single component."""
    issues = []
    
    try:
        # Check if component exists in web-types
        quasar_props = extract_quasar_props(comp_name, web_types)
        if not quasar_props:
            issues.append(f"Component {comp_name} not found in Quasar web-types")
            return issues
        
        # Check version compatibility
        config = load_config()
        if version.parse(config['quasar_version']) > version.parse("2.0.0"):
            issues.append(
                f"Component {comp_name} requires Quasar {config['quasar_version']} "
                f"but project uses 2.0.0"
            )
        
        # Check properties
        if "quasar_props" in component_data:
            missing_props, extra_props = compare_props(quasar_props, component_data["quasar_props"])
            
            if missing_props:
                issues.append(f"Missing Quasar properties: {', '.join(sorted(missing_props))}")
            if extra_props:
                issues.append(f"Extra properties not in Quasar docs: {', '.join(sorted(extra_props))}")
    
    except Exception as e:
        issues.append(f"Failed to verify {comp_name}: {str(e)}")
    
    return issues

def verify_components(component_files: list[str]) -> dict:
    """Verify component properties against Quasar web-types."""
    issues = {}
    
    try:
        # Load web-types once for all components
        web_types = get_web_types()
        
        for file_path in component_files:
            if not os.path.exists(file_path):
                continue
            
            with open(file_path, 'r') as f:
                try:
                    component_data = json.load(f)
                except json.JSONDecodeError:
                    issues[os.path.basename(file_path)] = ["Invalid JSON format"]
                    continue
            
            # Check Quasar components
            if "quasar_components" in component_data:
                file_issues = []
                for quasar_comp in component_data["quasar_components"]:
                    if isinstance(quasar_comp, dict):
                        comp_name = quasar_comp["name"]
                        comp_url = quasar_comp["url"].rstrip('/')
                    else:
                        comp_name = quasar_comp.rstrip(',')  # Remove trailing comma if present
                        comp_url = get_quasar_url(comp_name)
                    
                    comp_issues = verify_component(comp_name, comp_url, component_data, web_types)
                    if comp_issues:
                        file_issues.extend(comp_issues)
                
                if file_issues:
                    issues[os.path.basename(file_path)] = file_issues
    
    except Exception as e:
        print(f"Error during verification: {str(e)}")
        return {"error": [str(e)]}
    
    return issues

def verify_component_sync(component_file: str) -> list[str]:
    """Verify a single component file."""
    result = verify_components([component_file])
    return result.get(os.path.basename(component_file), [])
