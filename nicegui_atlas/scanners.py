"""Component scanners for NiceGUI Atlas."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from .models import (
    ArgumentInfo,
    CategoryInfo,
    ComponentIndex,
    ComponentInfo,
    EventInfo,
    FunctionInfo,
    PropertyInfo,
)


def scan_nicegui_categories(categories_data: dict) -> Dict[str, CategoryInfo]:
    """Convert NiceGUI categories data to CategoryInfo objects."""
    categories = {}
        
    for category in categories_data.get("categories", []):
        categories[category["id"]] = CategoryInfo(
            name=category["name"],
            description=category["description"],
            components=[],  # Will be populated when scanning components
            subcategories={}
        )
    
    return categories


def convert_nicegui_event(event_data: dict) -> EventInfo:
    """Convert NiceGUI event data to EventInfo model."""
    # Parse argument string into structured data
    # Example: "ClickEventArguments(sender=self, client=self.client)"
    arg_str = event_data.get("arguments", "")
    arguments = []
    if arg_str:
        # Basic parsing of argument string
        arg_parts = arg_str.strip("()").split(",")
        for part in arg_parts:
            if "=" in part:
                name, value = part.strip().split("=")
                arguments.append(ArgumentInfo(
                    name=name,
                    type="Any",  # We'd need more sophisticated parsing to determine type
                    description=None
                ))
    
    return EventInfo(
        name=event_data.get("name", ""),
        description=event_data.get("description", ""),
        arguments=arguments
    )


def convert_nicegui_method(method_data: dict, method_name: str) -> FunctionInfo:
    """Convert NiceGUI method data to FunctionInfo model."""
    arguments = []
    if "arguments" in method_data:
        # Similar argument parsing as events
        arg_str = method_data["arguments"]
        arg_parts = arg_str.strip("()").split(",")
        for part in arg_parts:
            if "=" in part:
                name, value = part.strip().split("=")
                arguments.append(ArgumentInfo(
                    name=name,
                    type="Any",
                    description=None
                ))
    
    return FunctionInfo(
        name=method_name,
        description=method_data.get("description", ""),
        arguments=arguments,
        return_type=method_data.get("returns")
    )


def scan_nicegui_component(data: dict) -> Optional[ComponentInfo]:
    """Convert NiceGUI component data to ComponentInfo."""
    
    # Convert properties
    properties = {}
    for prop_name, prop_data in data.get("python_props", {}).get("__init__", {}).items():
        properties[prop_name] = PropertyInfo(
            name=prop_name,
            type=prop_data.get("type", "Any"),
            description=prop_data.get("description"),
            default=prop_data.get("default"),
            required="default" not in prop_data
        )
    
    # Convert events
    events = {}
    for event_data in data.get("events", {}).get("__init__", {}).values():
        event_info = convert_nicegui_event(event_data)
        events[event_info.name] = event_info
    
    # Convert methods
    functions = {}
    for method_name, method_data in data.get("events", {}).get("methods", {}).items():
        function_info = convert_nicegui_method(method_data, method_name)
        functions[method_name] = function_info
    
    # Get documentation URL from first Quasar component if available
    # Get documentation URL from first Quasar component if available
    doc_url = None
    quasar_components = data.get("quasar_components", [])
    if quasar_components and isinstance(quasar_components[0], dict):
        doc_url = quasar_components[0].get("url")
    
    return ComponentInfo(
        name=data["name"],
        type="nicegui",
        description=data.get("description"),
        doc_url=doc_url,
        properties=properties,
        events=events,
        functions=functions,
        category=data.get("category")
    )


def scan_nicegui_components(component_files: Dict[str, dict]) -> Dict[str, ComponentInfo]:
    """Convert NiceGUI component data to ComponentInfo objects."""
    components = {}
    for file_path, data in component_files.items():
        if not any(skip in file_path for skip in ["categories.json", "component_mappings.json", "template.json"]):
            component = scan_nicegui_component(data)
            if component:
                components[component.name] = component
    
    return components


def create_nicegui_index(db_path: str = "db") -> ComponentIndex:
    """Create a complete index of NiceGUI components."""
    # Load all files into memory first
    db_dir = Path(db_path)
    
    # Load categories
    with open(db_dir / "categories.json") as f:
        categories_data = json.load(f)
    
    # Load all component files
    component_files = {}
    for subdir in db_dir.iterdir():
        if subdir.is_dir():
            for file_path in subdir.glob("*.json"):
                with open(file_path) as f:
                    component_files[str(file_path)] = json.load(f)
    
    # Convert to our models
    categories = scan_nicegui_categories(categories_data)
    components = scan_nicegui_components(component_files)
    
    # Add components to their categories
    for component in components.values():
        if component.category:
            # Find category ID by name
            for cat_id, cat_info in categories.items():
                if cat_info.name == component.category:
                    cat_info.components.append(component.name)
                    break
    
    return ComponentIndex(
        type="nicegui",
        version="1.0.0",  # TODO: Get actual version
        categories=categories,
        components=components
    )


def scan_quasar_component(tag_data: dict) -> ComponentInfo:
    """Convert Quasar web-types tag data to ComponentInfo."""
    properties = {}
    for attr in tag_data.get("attributes", []):
        name = attr.get("name", "")
        if name:
            value_info = attr.get("value", {})
            properties[name] = PropertyInfo(
                name=name,
                type=value_info.get("type", ""),
                description=attr.get("description", ""),
                default=attr.get("default"),
                required=attr.get("required", False),
                doc_url=attr.get("doc-url")
            )
    
    events = {}
    for event in tag_data.get("events", []):
        name = event.get("name", "")
        if name:
            arguments = []
            for arg in event.get("arguments", []):
                arguments.append(ArgumentInfo(
                    name=arg.get("name", ""),
                    type=arg.get("type", ""),
                    description=arg.get("description")
                ))
            events[name] = EventInfo(
                name=name,
                description=event.get("description", ""),
                arguments=arguments
            )
    
    # Get doc URL from first property that has it
    doc_url = None
    for prop in properties.values():
        if prop.doc_url:
            doc_url = prop.doc_url
            break
    
    return ComponentInfo(
        name=tag_data["name"],
        type="quasar",
        description=tag_data.get("description"),
        doc_url=doc_url,
        properties=properties,
        events=events,
        functions={},  # Quasar web-types don't include methods
        category=None  # We'll need to determine categories separately
    )


def create_quasar_index(web_types: dict, version: str = "2.16.9") -> ComponentIndex:
    """Create a complete index of Quasar components."""
    components = {}
    categories = {}  # TODO: Define Quasar categories
    
    # Convert all tags to components
    for tag in web_types.get("contributions", {}).get("html", {}).get("tags", []):
        if tag.get("name", "").startswith("Q"):
            component = scan_quasar_component(tag)
            components[component.name] = component
    
    return ComponentIndex(
        type="quasar",
        version=version,
        categories=categories,
        components=components
    )
