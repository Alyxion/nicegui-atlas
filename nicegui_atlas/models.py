"""Shared data models for NiceGUI Atlas."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ArgumentInfo(BaseModel):
    """Information about a function/event argument."""
    name: str
    type: str
    description: Optional[str] = None
    default: Optional[str] = None
    required: bool = False


class PropertyInfo(BaseModel):
    """Information about a component property."""
    name: str
    type: str
    description: Optional[str] = None
    default: Optional[str] = None
    required: bool = False
    doc_url: Optional[str] = None


class EventInfo(BaseModel):
    """Information about a component event."""
    name: str
    description: Optional[str] = None
    arguments: List[ArgumentInfo] = Field(default_factory=list)
    doc_url: Optional[str] = None


class FunctionInfo(BaseModel):
    """Information about a component function/method."""
    name: str
    description: Optional[str] = None
    arguments: List[ArgumentInfo] = Field(default_factory=list)
    return_type: Optional[str] = None
    doc_url: Optional[str] = None


class ComponentInfo(BaseModel):
    """Unified component information model."""
    name: str
    type: str = Field(..., description="Type of component (nicegui/quasar)")
    description: Optional[str] = None
    doc_url: Optional[str] = None
    properties: Dict[str, PropertyInfo] = Field(default_factory=dict)
    events: Dict[str, EventInfo] = Field(default_factory=dict)
    functions: Dict[str, FunctionInfo] = Field(default_factory=dict)
    category: Optional[str] = None


class CategoryInfo(BaseModel):
    """Category information model."""
    name: str
    description: Optional[str] = None
    components: List[str] = Field(default_factory=list)
    subcategories: Dict[str, 'CategoryInfo'] = Field(default_factory=dict)


class ComponentIndex(BaseModel):
    """Index of all components."""
    type: str = Field(..., description="Type of index (nicegui/quasar)")
    version: str
    categories: Dict[str, CategoryInfo] = Field(default_factory=dict)
    components: Dict[str, ComponentInfo] = Field(default_factory=dict)


def create_nicegui_index() -> ComponentIndex:
    """Create an index of all NiceGUI components."""
    # TODO: Implement scanning of NiceGUI components
    # This will involve:
    # 1. Reading the db/categories.json
    # 2. Scanning all component JSON files in db/
    # 3. Converting the data to our unified models
    return ComponentIndex(
        type="nicegui",
        version="1.0.0",  # TODO: Get actual version
        categories={},
        components={}
    )


def create_quasar_index(version: str = "2.16.9") -> ComponentIndex:
    """Create an index of all Quasar components."""
    # TODO: Implement scanning of Quasar components
    # This will involve:
    # 1. Getting the web-types data
    # 2. Converting it to our unified models
    # 3. Organizing components into categories
    return ComponentIndex(
        type="quasar",
        version=version,
        categories={},
        components={}
    )


def get_component_info(component_name: str, type: str = "nicegui") -> Optional[ComponentInfo]:
    """Get information about a specific component.
    
    Args:
        component_name: Name of the component
        type: Type of component ("nicegui" or "quasar")
    
    Returns:
        ComponentInfo if found, None otherwise
    """
    if type == "nicegui":
        # TODO: Implement NiceGUI component info retrieval
        pass
    elif type == "quasar":
        # TODO: Implement Quasar component info retrieval
        pass
    return None


def search_components(query: str, type: Optional[str] = None) -> List[ComponentInfo]:
    """Search for components by name or description.
    
    Args:
        query: Search query
        type: Optional type filter ("nicegui" or "quasar")
    
    Returns:
        List of matching components
    """
    # TODO: Implement component search
    return []
