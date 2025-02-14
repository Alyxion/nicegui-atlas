"""Component registry that holds all NiceGUI and Quasar component data in memory."""

import json
from pathlib import Path
from typing import Dict, Optional

from .models import ComponentIndex, ComponentInfo
from .scanners import create_nicegui_index, create_quasar_index


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
            self._nicegui_index: Optional[ComponentIndex] = None
            self._quasar_index: Optional[ComponentIndex] = None
            self._quasar_web_types: Optional[dict] = None
            self._initialized = True
    
    def initialize(self, db_path: str = "db"):
        """Load all component data into memory."""
        # Load NiceGUI component data
        self._nicegui_index = create_nicegui_index(db_path)
        
        # Load Quasar web-types data
        from .quasar_verifier import get_cached_web_types
        self._quasar_web_types = get_cached_web_types()
        
        # Create Quasar index
        self._quasar_index = create_quasar_index(self._quasar_web_types)
    
    @property
    def nicegui_index(self) -> ComponentIndex:
        """Get the NiceGUI component index."""
        if self._nicegui_index is None:
            self.initialize()
        return self._nicegui_index
    
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
    
    def get_nicegui_component(self, name: str) -> Optional['ComponentInfo']:
        """Get a NiceGUI component by name."""
        return self.nicegui_index.components.get(name)
    
    def get_quasar_component(self, name: str) -> Optional['ComponentInfo']:
        """Get a Quasar component by name."""
        # Ensure Q prefix
        if not name.startswith("Q"):
            name = "Q" + name
        return self.quasar_index.components.get(name)
    
    def get_component(self, name: str, type: str = "nicegui") -> Optional['ComponentInfo']:
        """Get a component by name and type."""
        if type == "nicegui":
            return self.get_nicegui_component(name)
        elif type == "quasar":
            return self.get_quasar_component(name)
        return None


# Global registry instance
registry = ComponentRegistry()
