"""Command for extracting event types from NiceGUI components."""

import argparse
import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, Callable, get_args, get_origin
import collections.abc

import nicegui.elements
import nicegui.events
from nicegui.element import Element
from nicegui.elements.mixins.disableable_element import DisableableElement
from nicegui.elements.mixins.value_element import ValueElement

from .base import CommandPlugin, registry as command_registry


def get_all_subclasses(cls: type) -> Set[type]:
    """Recursively return all subclasses of a class."""
    subclasses = set(cls.__subclasses__())
    for subclass in list(subclasses):
        subclasses |= get_all_subclasses(subclass)
    return subclasses


def extract_event_types_from_hint(type_hint: Any) -> Set[type]:
    """
    Recursively extract event types from a type hint.
    
    Event types are assumed to be classes whose names end with 'EventArguments'.
    """
    result = set()
    if inspect.isclass(type_hint) and type_hint.__name__.endswith("EventArguments"):
        result.add(type_hint)
    else:
        origin = get_origin(type_hint)
        if origin is None:
            # Example: Optional[Handler[SomeEventArguments]]
            if hasattr(type_hint, '__origin__') and type_hint.__origin__.__name__ == 'Handler':
                args = get_args(type_hint)
                if args and inspect.isclass(args[0]) and args[0].__name__.endswith("EventArguments"):
                    result.add(args[0])
        elif origin is Union:
            for arg in get_args(type_hint):
                if arg is not type(None):
                    result |= extract_event_types_from_hint(arg)
        elif origin in (Callable, collections.abc.Callable):
            args = get_args(type_hint)
            if args:
                event_args = args[0]
                if isinstance(event_args, (tuple, list)):
                    for event_arg in event_args:
                        if inspect.isclass(event_arg) and event_arg.__name__.endswith("EventArguments"):
                            result.add(event_arg)
                else:
                    if inspect.isclass(event_args) and event_args.__name__.endswith("EventArguments"):
                        result.add(event_args)
    return result


class EventExtractor:
    """Extracts event types from NiceGUI components."""
    
    def __init__(self):
        self.events_dir = Path('db/events')
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.event_types: Dict[str, Dict[str, Any]] = {}
        self._discover_event_types()
    
    def _discover_event_types(self) -> None:
        """Discover all event argument classes from nicegui.events."""
        self.event_classes = {
            name: item
            for name, item in vars(nicegui.events).items()
            if inspect.isclass(item) and name.endswith('EventArguments') and hasattr(item, '__init__')
        }
    
    def extract_events(self, filter_class: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Extract event types from all NiceGUI element classes."""
        for cls in self._get_element_classes():
            if filter_class and filter_class.lower() not in cls.__name__.lower():
                continue
            self._extract_class_events(cls)
        return self.event_types
    
    def _get_element_classes(self) -> List[type]:
        """
        Return all subclasses of Element (excluding some base classes)
        using a recursive search.
        """
        excluded = {Element, DisableableElement, ValueElement}
        return [cls for cls in get_all_subclasses(Element) if cls not in excluded]
    
    def _extract_class_events(self, cls: type) -> None:
        """Extract event types from a given class by examining __init__ and event methods."""
        try:
            # Process __init__ parameters
            init_sig = inspect.signature(cls.__init__)
            for param in init_sig.parameters.values():
                if param.name.startswith('on_'):
                    for event_type in extract_event_types_from_hint(param.annotation):
                        self._add_event_type(event_type, cls.__name__)
            
            # Process methods with names starting with 'on_'
            for _, member in inspect.getmembers(cls, predicate=inspect.isfunction):
                if member.__name__.startswith('on_'):
                    sig = inspect.signature(member)
                    for param in sig.parameters.values():
                        if param.name == 'callback':
                            for event_type in extract_event_types_from_hint(param.annotation):
                                self._add_event_type(event_type, cls.__name__)
        except (ValueError, TypeError):
            # Ignore classes with signature problems
            pass
    
    def _add_event_type(self, event_type: type, component_name: str) -> None:
        """Add an event type to the collection if not already present."""
        event_type_name = event_type.__name__
        if event_type_name not in self.event_types:
            # Gather information about the event's fields from its __init__ signature.
            fields = {}
            for name, field in inspect.signature(event_type.__init__).parameters.items():
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
                'arguments': fields
            }
    
    def update_event_jsons(self) -> None:
        """Update event JSON files in the events directory."""
        # Preserve any existing manual changes.
        existing_events = {}
        for file in self.events_dir.glob('*.json'):
            if file.name != 'event_base.json':
                with open(file) as f:
                    existing_events[file.stem] = json.load(f)
        
        for event_type, data in self.event_types.items():
            # Convert event type name (minus the suffix) to snake_case filename.
            filename = ''.join(['_' + c.lower() if c.isupper() else c for c in event_type[:-14]]).lstrip('_') + '.json'
            filepath = self.events_dir / filename
            if filepath.stem in existing_events:
                existing = existing_events[filepath.stem]
                existing.update({'arguments': data['arguments']})
                data = existing
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)


class ExtractEventsCommand(CommandPlugin):
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
        extractor = EventExtractor()
        events = extractor.extract_events(args.filter if hasattr(args, 'filter') else None)
        for event_type, data in sorted(events.items()):
            print(f"\n{event_type}:")
            print("  Arguments:")
            for arg_name, arg_info in sorted(data['arguments'].items()):
                req = " (required)" if arg_info['required'] else ""
                print(f"    - {arg_name}: {arg_info['type']}{req}")
        extractor.update_event_jsons()
        print("Done!")


# Register the command plugin.
command_registry.register(ExtractEventsCommand())
