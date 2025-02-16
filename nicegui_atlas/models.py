"""Shared data models for NiceGUI Atlas."""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class Example(BaseModel):
    """Example usage of a property, event, or function."""
    code: str
    description: Optional[str] = None


class ArgumentInfo(BaseModel):
    """Information about a function/event argument."""
    name: str
    type: str
    description: Optional[str] = None
    default: Optional[str] = None
    required: bool = False
    examples: List[Example] = Field(default_factory=list)


class PropertyInfo(BaseModel):
    """Information about a component property."""
    name: str
    type: str
    description: Optional[str] = None
    default: Optional[str] = None
    required: bool = False
    doc_url: Optional[str] = None
    examples: List[Example] = Field(default_factory=list)
    quasar_prop: Optional[str] = None  # For NiceGUI properties that map to Quasar props


class EventInfo(BaseModel):
    """Information about a component event."""
    name: str
    description: Optional[str] = None
    arguments: List[ArgumentInfo] = Field(default_factory=list)
    doc_url: Optional[str] = None
    examples: List[Example] = Field(default_factory=list)


class FunctionInfo(BaseModel):
    """Information about a component function/method."""
    name: str
    description: Optional[str] = None
    arguments: List[ArgumentInfo] = Field(default_factory=list)
    return_type: Optional[str] = None
    doc_url: Optional[str] = None
    examples: List[Example] = Field(default_factory=list)


class LibraryInfo(BaseModel):
    """Information about a required library."""
    name: str
    version: Optional[str] = None
    url: Optional[str] = None


class QuasarComponentInfo(BaseModel):
    """Information about a linked Quasar component."""
    name: str
    url: Optional[str] = None


class LibraryChecksum(BaseModel):
    """Information about a library file's checksum."""
    path: str
    checksum: str


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
    examples: List[Example] = Field(default_factory=list)
    # NiceGUI specific fields
    source_path: Optional[str] = None
    direct_ancestors: List[str] = Field(default_factory=list)
    quasar_components: List[Union[str, QuasarComponentInfo]] = Field(default_factory=list)
    libraries: List[LibraryInfo] = Field(default_factory=list)
    internal_components: List[str] = Field(default_factory=list)
    html_element: Optional[str] = None
    js_file: Optional[str] = None
    # Checksum fields
    py_checksum: Optional[str] = None
    js_checksum: Optional[str] = None
    lib_checksums: List[LibraryChecksum] = Field(default_factory=list)


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


class EventTypeInfo(BaseModel):
    """Information about an event type."""
    name: str
    description: str
    type: str = "event"
    arguments: Dict[str, ArgumentInfo] = Field(default_factory=dict)
    ancestors: List[str] = Field(default_factory=list)
