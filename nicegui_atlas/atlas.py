"""Component Atlas - Access to NiceGUI component information."""

import json
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Set


@dataclass
class CategoryInfo:
    """Information about a component category."""
    id: str
    name: str
    priority: int
    description: str


@dataclass
class ComponentInfo:
    """Information about a NiceGUI component."""
    name: str
    category: str
    description: str
    source_path: str
    direct_ancestors: Optional[List[str]] = None
    quasar_components: Optional[List[str]] = None
    libraries: Optional[List[Dict[str, str]]] = None
    internal_components: Optional[List[str]] = None
    html_element: Optional[str] = None
    js_file: Optional[str] = None

    @classmethod
    def from_json(cls, data: dict) -> 'ComponentInfo':
        """Create a ComponentInfo instance from JSON data."""
        return cls(**data)


class ComponentAtlas:
    """Access to NiceGUI component information."""
    
    _components: Dict[str, ComponentInfo] = {}
    _categories: Dict[str, List[ComponentInfo]] = {}
    _category_info: Dict[str, CategoryInfo] = {}
    _initialized: bool = False
    
    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure the atlas is initialized."""
        if cls._initialized:
            return
        
        # Get the db directory path (in root of package)
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_dir = os.path.join(package_dir, "db")
        
        # Load category definitions
        with open(os.path.join(db_dir, "categories.json")) as f:
            categories_data = json.load(f)
            for category in categories_data["categories"]:
                cls._category_info[category["id"]] = CategoryInfo(**category)
                cls._categories[category["id"]] = []
        
        # Load all component JSON files
        for category in os.listdir(db_dir):
            category_dir = os.path.join(db_dir, category)
            if not os.path.isdir(category_dir) or category == "bak":
                continue
                
            for file in os.listdir(category_dir):
                if not file.endswith(".json"):
                    continue
                    
                with open(os.path.join(category_dir, file)) as f:
                    data = json.load(f)
                    component = ComponentInfo.from_json(data)
                    # Store by both full name and short name
                    cls._components[component.name] = component
                    cls._components[component.name.split('.')[-1]] = component
                    cls._categories[category].append(component)
        
        cls._initialized = True
    
    @classmethod
    def get_component(cls, name: str) -> Optional[ComponentInfo]:
        """Get information about a specific component."""
        cls._ensure_initialized()
        # Handle both full name (nicegui.ui.button) and short name (ui.button)
        if name.startswith('nicegui.'):
            lookup_name = name
        elif name.startswith('ui.'):
            lookup_name = f"nicegui.{name}"
        else:
            lookup_name = name
        return cls._components.get(lookup_name)
    
    @classmethod
    def get_category(cls, category: str) -> List[ComponentInfo]:
        """Get all components in a category."""
        cls._ensure_initialized()
        return cls._categories.get(category, [])
    
    @classmethod
    def get_category_info(cls, category: str) -> Optional[CategoryInfo]:
        """Get information about a category."""
        cls._ensure_initialized()
        return cls._category_info.get(category)
    
    @classmethod
    def get_categories(cls) -> List[CategoryInfo]:
        """Get all available categories, sorted by priority."""
        cls._ensure_initialized()
        return sorted(
            cls._category_info.values(),
            key=lambda x: (-x.priority, x.name)  # Sort by priority (high to low), then name
        )
    
    @classmethod
    def search(cls, query: str) -> List[ComponentInfo]:
        """Search components by name or description."""
        cls._ensure_initialized()
        query = query.lower()
        results = []
        
        for component in cls._components.values():
            if (query in component.name.lower() or 
                query in component.description.lower()):
                results.append(component)
        
        return sorted(results, key=lambda x: x.name)
    
    @classmethod
    def get_all_components(cls) -> List[ComponentInfo]:
        """Get all available components."""
        cls._ensure_initialized()
        return sorted(cls._components.values(), key=lambda x: x.name)
