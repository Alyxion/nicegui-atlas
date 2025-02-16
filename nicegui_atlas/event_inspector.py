"""Event argument type inspector for NiceGUI events."""

import inspect
from typing import Dict, List, Optional, get_type_hints

from nicegui.events import (
    ClickEventArguments,
    EventArguments,
    ValueChangeEventArguments,
)

from .models import ArgumentInfo


def get_event_class_info() -> Dict[str, List[ArgumentInfo]]:
    """Get information about all event argument classes in nicegui.events."""
    event_info = {}
    
    # Define standard event arguments
    event_info['ClickEventArguments'] = [
        ArgumentInfo(name='sender', type='Element', description='The element that triggered the event'),
        ArgumentInfo(name='client', type='Client', description='The client that triggered the event'),
    ]
    
    event_info['ValueChangeEventArguments'] = [
        ArgumentInfo(name='sender', type='Element', description='The element that triggered the event'),
        ArgumentInfo(name='client', type='Client', description='The client that triggered the event'),
        ArgumentInfo(name='value', type='Any', description='The new value'),
    ]
    
    event_info['EventArguments'] = [
        ArgumentInfo(name='sender', type='Element', description='The element that triggered the event'),
        ArgumentInfo(name='client', type='Client', description='The client that triggered the event'),
    ]
    
    return event_info


def get_event_arguments(event_class_name: str) -> List[ArgumentInfo]:
    """Get argument information for a specific event class."""
    # Initialize event info cache if needed
    if not hasattr(get_event_arguments, '_event_info'):
        get_event_arguments._event_info = get_event_class_info()
    
    # Return cached info for the event class
    return get_event_arguments._event_info.get(event_class_name, [])
