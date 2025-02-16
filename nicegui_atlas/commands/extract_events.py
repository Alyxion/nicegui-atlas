"""Command for extracting event types from NiceGUI components."""

import argparse
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Callable, get_args, get_origin, Tuple
import collections.abc  # <-- Import collections.abc

import nicegui.elements
import nicegui.events
from nicegui.element import Element
from nicegui.elements.mixins.disableable_element import DisableableElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import CommandPlugin, registry as command_registry


def debug_type_hint(type_hint: Any, prefix: str = "") -> None:
    """Debug helper to print detailed information about a type hint."""
    print(f"{prefix}Type hint: {type_hint}")
    print(f"{prefix}Type: {type(type_hint)}")
    print(f"{prefix}Has __origin__: {hasattr(type_hint, '__origin__')}")
    if hasattr(type_hint, '__origin__'):
        print(f"{prefix}Origin: {type_hint.__origin__}")
        print(f"{prefix}Args: {get_args(type_hint)}")
        for i, arg in enumerate(get_args(type_hint)):
            print(f"{prefix}  Arg {i}: {arg} (type: {type(arg)})")
            if hasattr(arg, '__origin__'):
                print(f"{prefix}    Origin: {arg.__origin__}")
                print(f"{prefix}    Args: {get_args(arg)}")
                for j, inner_arg in enumerate(get_args(arg)):
                    print(f"{prefix}      Inner arg {j}: {inner_arg} (type: {type(inner_arg)})")


class EventExtractor:
    """Extracts event types from NiceGUI components."""
    
    def __init__(self):
        """Initialize event extractor."""
        self.events_dir = Path('db/events')
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.event_types = {}
        self._discover_event_types()
    
    def _discover_event_types(self) -> None:
        """Discover all event argument types from nicegui.events."""
        self.event_classes = {}
        print("\nDiscovering event types from nicegui.events...")
        for name in dir(nicegui.events):
            item = getattr(nicegui.events, name)
            if (inspect.isclass(item) and 
                name.endswith('EventArguments') and
                hasattr(item, '__init__')):
                print(f"  Found event type: {name}")
                self.event_classes[name] = item
        print(f"Discovered {len(self.event_classes)} event types")
    
    def extract_events(self, filter_class: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Extract all event types from NiceGUI components."""
        # Get all NiceGUI element classes
        print("\nGetting NiceGUI element classes...")
        element_classes = self._get_element_classes()
        print(f"Found {len(element_classes)} element classes")
        
        # Extract event types from each class
        print("\nExtracting events from classes...")
        for cls in element_classes:
            if filter_class and filter_class.lower() not in cls.__name__.lower():
                continue
            print(f"\nChecking {cls.__name__}...")
            self._extract_class_events(cls)
        
        return self.event_types
    
    def _get_element_classes(self) -> List[type]:
        """Get all NiceGUI element classes."""
        classes = set()
        
        # Add base classes and mixins
        print("  Adding base classes and mixins...")
        classes.add(Element)
        classes.add(DisableableElement)
        classes.add(ValueElement)
        
        # Get all element classes from nicegui.elements
        print("  Scanning nicegui.elements...")
        for name in dir(nicegui.elements):
            if name.startswith('_'):  # Skip private/internal modules
                continue
            try:
                module = getattr(nicegui.elements, name)
                if inspect.ismodule(module):
                    # If it's a module, look for classes in it
                    for cls_name in dir(module):
                        if cls_name.startswith('_'):
                            continue
                        try:
                            cls = getattr(module, cls_name)
                            if (inspect.isclass(cls) and 
                                issubclass(cls, Element) and
                                cls not in (Element, DisableableElement, ValueElement)):
                                print(f"    Found element class: {cls.__name__}")
                                classes.add(cls)
                        except (TypeError, AttributeError) as e:
                            print(f"    Error processing {name}.{cls_name}: {e}")
                elif (inspect.isclass(module) and 
                      issubclass(module, Element) and
                      module not in (Element, DisableableElement, ValueElement)):
                    print(f"    Found element class: {name}")
                    classes.add(module)
            except (TypeError, AttributeError) as e:
                print(f"    Error processing {name}: {e}")
        
        return list(classes)
    
    def _extract_class_events(self, cls: type) -> None:
        """Extract event types from a class."""
        try:
            # Check __init__ parameters
            print(f"  Checking __init__ parameters...")
            init_sig = inspect.signature(cls.__init__)
            for param_name, param in init_sig.parameters.items():
                if param_name.startswith('on_'):
                    print(f"    Found event parameter: {param_name}")
                    debug_type_hint(param.annotation, "      ")
                    self._process_type_hint(param.annotation, cls.__name__, param_name)
            
            # Check methods
            print(f"  Checking methods...")
            for name, member in inspect.getmembers(cls):
                if name.startswith('on_') and inspect.isfunction(member):
                    print(f"    Found event method: {name}")
                    sig = inspect.signature(member)
                    for param in sig.parameters.values():
                        if param.name == 'callback':
                            print(f"      Found callback parameter with type: {param.annotation}")
                            debug_type_hint(param.annotation, "        ")
                            self._process_type_hint(param.annotation, cls.__name__, name)
        except (ValueError, TypeError) as e:
            print(f"  Error processing {cls.__name__}: {e}")
            pass
    
    def _process_type_hint(self, type_hint: Any, class_name: str, event_name: str) -> None:
        """Process a type hint to find event types."""
        print(f"\n    Processing type hint: {type_hint}")
        
        # Handle direct event types
        if (inspect.isclass(type_hint) and 
            hasattr(type_hint, '__name__') and 
            type_hint.__name__.endswith('EventArguments')):
            print(f"      Found direct event type: {type_hint.__name__}")
            self._add_event_type(type_hint, class_name, event_name)
            return
        
        # Get the origin type
        origin = get_origin(type_hint)
        if origin is None:
            # Handle Optional[Handler[EventArguments]] case
            if hasattr(type_hint, '__origin__') and type_hint.__origin__.__name__ == 'Handler':
                args = get_args(type_hint)
                if args and hasattr(args[0], '__name__') and args[0].__name__.endswith('EventArguments'):
                    print(f"      Found Handler event type: {args[0].__name__}")
                    self._add_event_type(args[0], class_name, event_name)
            return
        
        print(f"      Origin type: {origin}")
        
        # Handle Union types (including Optional)
        if origin is Union:
            print("      Processing Union type")
            for arg in get_args(type_hint):
                if arg is not type(None):  # Skip NoneType
                    print(f"        Union arg: {arg}")
                    # Handle Callable inside Union
                    if hasattr(arg, '__origin__') and arg.__origin__ in (Callable, collections.abc.Callable):
                        print("        Found Callable in Union")
                        callable_args = get_args(arg)
                        if callable_args and len(callable_args) >= 1:
                            event_args = callable_args[0]
                            print(f"        Callable args: {event_args}")
                            if isinstance(event_args, (tuple, list)):
                                print("        Processing tuple/list of arguments")
                                for event_arg in event_args:
                                    if (inspect.isclass(event_arg) and 
                                        hasattr(event_arg, '__name__') and 
                                        event_arg.__name__.endswith('EventArguments')):
                                        print(f"        Found event type in tuple/list: {event_arg.__name__}")
                                        self._add_event_type(event_arg, class_name, event_name)
                            else:
                                if (inspect.isclass(event_args) and 
                                    hasattr(event_args, '__name__') and 
                                    event_args.__name__.endswith('EventArguments')):
                                    print(f"        Found event type: {event_args.__name__}")
                                    self._add_event_type(event_args, class_name, event_name)
                    else:
                        self._process_type_hint(arg, class_name, event_name)
        
        # Handle Callable types
        elif origin in (Callable, collections.abc.Callable):
            print("      Processing Callable type")
            args = get_args(type_hint)
            if len(args) >= 1:  # Has arguments
                event_args = args[0]  # First argument is usually the event argument type
                print(f"      Callable args: {event_args}")
                if isinstance(event_args, (tuple, list)):
                    print("      Processing tuple/list of arguments")
                    for event_arg in event_args:
                        if (inspect.isclass(event_arg) and 
                            hasattr(event_arg, '__name__') and 
                            event_arg.__name__.endswith('EventArguments')):
                            print(f"      Found event type in tuple/list: {event_arg.__name__}")
                            self._add_event_type(event_arg, class_name, event_name)
                else:
                    if (inspect.isclass(event_args) and 
                        hasattr(event_args, '__name__') and 
                        event_args.__name__.endswith('EventArguments')):
                        print(f"      Found event type: {event_args.__name__}")
                        self._add_event_type(event_args, class_name, event_name)
    
    def _add_event_type(self, event_type: object, class_name: str, event_name: str) -> None:
        """Add an event type to the collection. Accepts either a type or a string as event_type."""
        if isinstance(event_type, type):
            event_type_name = event_type.__name__
            event_class = event_type
        else:
            event_type_name = event_type
            event_class = self.event_classes.get(event_type_name)
            if not event_class:
                import nicegui.events
                event_class = getattr(nicegui.events, event_type_name, None)
                if not event_class:
                    print(f"        Event type {event_type_name} not found in discovered types")
                    return
        
        if event_type_name not in self.event_types:
            print(f"        Adding new event type: {event_type_name}")
            # Get field info from the class
            fields = {}
            for name, field in inspect.signature(event_class.__init__).parameters.items():
                if name not in ('self', 'args', 'kwargs'):
                    fields[name] = {
                        'name': name,
                        'type': str(field.annotation).replace('typing.', ''),
                        'description': f'The {name} value for the event',
                        'required': field.default is field.empty
                    }
            
            self.event_types[event_type_name] = {
                'name': event_type_name,
                'description': f'Arguments for {event_type_name.replace("EventArguments", "")} events',
                'type': 'event',
                'arguments': fields,
                'used_by': []
            }
        
        # Add usage information
        usage = {
            'component': class_name,
            'event': event_name
        }
        if usage not in self.event_types[event_type_name]['used_by']:
            print(f"        Adding usage: {class_name}.{event_name}")
            self.event_types[event_type_name]['used_by'].append(usage)
    
    def update_event_jsons(self) -> None:
        """Update event JSON files in the db/events directory."""
        # First read existing files to preserve any manual additions
        existing_events = {}
        for file in self.events_dir.glob('*.json'):
            if file.name != 'event_base.json':  # Skip base event file
                with open(file) as f:
                    existing_events[file.stem] = json.load(f)
        
        # Update event files
        for event_type, data in self.event_types.items():
            # Convert to snake_case for filename
            filename = ''.join(['_' + c.lower() if c.isupper() else c 
                              for c in event_type[:-14]]).lstrip('_') + '.json'
            filepath = self.events_dir / filename
            print(f"\nUpdating {filepath}")
            
            # Merge with existing data if present
            if filepath.stem in existing_events:
                existing_data = existing_events[filepath.stem]
                # Preserve existing fields but update arguments and add new usage info
                existing_data.update({
                    'arguments': data['arguments'],
                    'used_by': data['used_by']
                })
                data = existing_data
            
            # Write updated data
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)


class ExtractEventsCommand(CommandPlugin):
    """Command for extracting event types from NiceGUI components."""
    
    @property
    def name(self) -> str:
        return "extract_events"
    
    @property
    def help(self) -> str:
        return "Extract event types from NiceGUI components"
    
    @property
    def examples(self) -> List[str]:
        return [
            "Extract event types and update event JSONs:",
            "  python -m nicegui_atlas extract_events"
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--filter', help='Filter to specific class')
    
    def execute(self, args: argparse.Namespace) -> None:
        print("\nExtracting event types from NiceGUI components...")
        
        extractor = EventExtractor()
        events = extractor.extract_events(args.filter if hasattr(args, 'filter') else None)
        
        print(f"\nFound {len(events)} event types:")
        for event_type, data in sorted(events.items()):
            print(f"\n{event_type}:")
            print("  Arguments:")
            for arg_name, arg_info in sorted(data['arguments'].items()):
                required = " (required)" if arg_info['required'] else ""
                print(f"    - {arg_name}: {arg_info['type']}{required}")
            print("  Used by:")
            for usage in sorted(data['used_by'], key=lambda x: (x['component'], x['event'])):
                print(f"    - {usage['component']}.{usage['event']}")
        
        print("\nUpdating event JSON files...")
        extractor.update_event_jsons()
        print("Done!")


# Register the plugin
command_registry.register(ExtractEventsCommand())
