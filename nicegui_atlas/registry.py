"""Component registry that holds all NiceGUI and Quasar component data in memory."""

import json
from pathlib import Path
from typing import Dict, Optional

from .models import ComponentIndex, ComponentInfo
from .scanners import (
    create_nicegui_index,
    create_quasar_index,
    scan_nicegui_components,
)


class ComponentRegistry:
    """Singleton registry that holds all component data in memory."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ComponentRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._nicegui_index: Optional[Dict[str, ComponentInfo]] = None
            self._nicegui_component_index: Optional[ComponentIndex] = None
            self._quasar_index: Optional[ComponentIndex] = None
            self._quasar_web_types: Optional[dict] = None
            self._initialized = True
    
    def initialize(self, db_path: str = "db"):
        """Load all component data into memory."""
        # Load all files into memory first
        db_dir = Path(db_path)
        
        # Load categories and component files
        with open(db_dir / "categories.json") as f:
            categories_data = json.load(f)
        
        component_files = {}
        for subdir in db_dir.iterdir():
            if subdir.is_dir():
                for file_path in subdir.glob("*.json"):
                    with open(file_path) as f:
                        component_files[str(file_path)] = json.load(f)
        
        # Create NiceGUI indices
        nicegui_components = scan_nicegui_components(component_files)
        self._nicegui_index = nicegui_components
        self._nicegui_component_index = create_nicegui_index(db_path)
        
        # Load Quasar web-types data
        from .quasar_verifier import get_web_types
        self._quasar_web_types = get_web_types()
        
        # Create Quasar index
        self._quasar_index = create_quasar_index(self._quasar_web_types)
    
    @property
    def nicegui_component_index(self) -> ComponentIndex:
        """Get the NiceGUI component index."""
        if self._nicegui_component_index is None:
            self.initialize()
        return self._nicegui_component_index
    
    @property
    def quasar_index(self) -> ComponentIndex:
        """Get the Quasar component index."""
        if self._quasar_index is None:
            self.initialize()
        return self._quasar_index
    
    @property
    def quasar_web_types(self) -> dict:
        """Get the raw Quasar web-types data."""
        if self._quasar_web_types is None:
            self.initialize()
        return self._quasar_web_types
    
    def get_nicegui_component(self, name: str) -> Optional[ComponentInfo]:
        """Get a NiceGUI component by name."""
        if not self._nicegui_index:
            self.initialize()
        return self._nicegui_index.get(name)
    
    def get_quasar_component(self, name: str) -> Optional[ComponentInfo]:
        """Get a Quasar component by name."""
        if not self._quasar_index:
            self.initialize()
        # Ensure Q prefix
        if not name.startswith("Q"):
            name = "Q" + name
        return self._quasar_index.components.get(name)
    
    def get_component(self, name: str, type: str = "nicegui") -> Optional[ComponentInfo]:
        """Get a component by name and type."""
        if type == "nicegui":
            return self.get_nicegui_component(name)
        elif type == "quasar":
            return self.get_quasar_component(name)
        return None


# Global registry instance
registry = ComponentRegistry()
