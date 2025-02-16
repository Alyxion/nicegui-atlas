"""Command for verifying component documentation completeness."""

import argparse
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from nicegui import ui

from .base import CommandPlugin, registry as command_registry
from ..registry import ComponentRegistry
from ..models import ComponentInfo


# Force colors even when output is redirected
os.environ['FORCE_COLOR'] = '1'
os.environ['TERM'] = 'xterm-256color'


# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def format_type(type_str: str) -> str:
    """Format a type string to be more readable."""
    return type_str.replace('typing.', '').replace('nicegui.events.', '')


class ComponentVerifier:
    """Verifies component documentation completeness."""
    
    def __init__(self, json_path: str, component_class: type):
        """Initialize verifier with component JSON and class."""
        self.json_path = Path(json_path)
        self.component_class = component_class
        self.json_data = self._load_json()
    
    def _load_json(self) -> dict:
        """Load component JSON file."""
        with open(self.json_path) as f:
            return json.load(f)
    
    def find_undocumented_events(self) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
        """Find events that are not documented in the JSON and generate their documentation."""
        missing = {
            'init_params': [],  # (name, doc) tuples for __init__ parameters
            'methods': []       # (name, doc) tuples for methods
        }
        
        # Check __init__ parameters
        init_sig = inspect.signature(self.component_class.__init__)
        init_doc = inspect.getdoc(self.component_class.__init__) or ''
        param_docs = self._parse_docstring_params(init_doc)
        
        for param_name, param in init_sig.parameters.items():
            if param_name.startswith('on_'):
                event_name = param_name
                if not self._is_event_documented(event_name):
                    param_type = str(param.annotation).replace('typing.', '')
                    doc = {
                        "description": param_docs.get(param_name, f"Callback for {event_name.replace('on_', '')} events"),
                        "arguments": self._get_event_arguments(param_type)
                    }
                    missing['init_params'].append((event_name, doc))
        
        # Check methods
        for name, member in inspect.getmembers(self.component_class):
            if name.startswith('on_') and inspect.isfunction(member):
                event_name = name
                if not self._is_event_documented(event_name):
                    method_doc = inspect.getdoc(member) or ''
                    sig = inspect.signature(member)
                    param_type = next((str(p.annotation).replace('typing.', '') 
                                    for p in sig.parameters.values() 
                                    if p.name == 'callback'), 'Any')
                    doc = {
                        "description": method_doc.split('\n')[0] if method_doc else f"Add callback for {event_name.replace('on_', '')} events",
                        "arguments": self._get_event_arguments(param_type),
                        "returns": "Self (for method chaining)"
                    }
                    missing['methods'].append((event_name, doc))
        
        return missing
    
    def find_orphaned_events(self) -> Dict[str, List[str]]:
        """Find events in JSON that don't exist in the Python code."""
        orphaned = {
            'init_params': [],  # events in JSON __init__ but not in Python
            'methods': []       # events in JSON methods but not in Python
        }
        
        # Get all Python events
        init_events = {name for name in inspect.signature(self.component_class.__init__).parameters 
                      if name.startswith('on_')}
        method_events = {name for name, member in inspect.getmembers(self.component_class)
                        if name.startswith('on_') and inspect.isfunction(member)}
        
        # Check JSON events against Python
        events = self.json_data.get('events', {})
        if '__init__' in events:
            for event_name in events['__init__']:
                if event_name not in init_events:
                    orphaned['init_params'].append(event_name)
        
        if 'methods' in events:
            for event_name in events['methods']:
                if event_name not in method_events:
                    orphaned['methods'].append(event_name)
        
        return orphaned
    
    def get_component_info(self) -> Dict[str, Any]:
        """Get comprehensive component information."""
        init_sig = inspect.signature(self.component_class.__init__)
        init_doc = inspect.getdoc(self.component_class.__init__) or ''
        param_docs = self._parse_docstring_params(init_doc)
        
        info = {
            'name': self.component_class.__name__,
            'doc': inspect.getdoc(self.component_class) or '',
            'init_params': [],
            'events': {
                'init': [],
                'methods': []
            },
            'properties': []
        }
        
        # Get init parameters
        for name, param in init_sig.parameters.items():
            if name not in ('self', 'args', 'kwargs'):
                param_info = {
                    'name': name,
                    'type': str(param.annotation).replace('typing.', ''),
                    'default': str(param.default) if param.default is not param.empty else None,
                    'doc': param_docs.get(name, '')
                }
                if name.startswith('on_'):
                    info['events']['init'].append(param_info)
                else:
                    info['init_params'].append(param_info)
        
        # Get methods
        for name, member in inspect.getmembers(self.component_class):
            if name.startswith('on_') and inspect.isfunction(member):
                method_doc = inspect.getdoc(member) or ''
                info['events']['methods'].append({
                    'name': name,
                    'doc': method_doc.split('\n')[0] if method_doc else ''
                })
        
        return info
    
    def _parse_docstring_params(self, docstring: str) -> Dict[str, str]:
        """Parse parameter descriptions from docstring."""
        param_docs = {}
        for line in docstring.split('\n'):
            line = line.strip()
            if line.startswith(':param '):
                parts = line[6:].split(':', 1)
                if len(parts) == 2:
                    param_name = parts[0].strip()
                    description = parts[1].strip()
                    param_docs[param_name] = description
        return param_docs
    
    def _get_event_arguments(self, type_hint: str) -> str:
        """Generate event arguments string based on type hint."""
        if 'UploadEventArguments' in type_hint:
            return "UploadEventArguments(sender=self, client=self.client, content=file, name=filename, type=content_type)"
        elif 'MultiUploadEventArguments' in type_hint:
            return "MultiUploadEventArguments(sender=self, client=self.client, contents=files, names=filenames, types=content_types)"
        elif 'UiEventArguments' in type_hint:
            return "UiEventArguments(sender=self, client=self.client)"
        elif 'ValueChangeEventArguments' in type_hint:
            return "ValueChangeEventArguments(sender=self, client=self.client, value=value)"
        elif 'ClickEventArguments' in type_hint:
            return "ClickEventArguments(sender=self, client=self.client)"
        else:
            return "EventArguments(sender=self, client=self.client)"
    
    def _is_event_documented(self, event_name: str) -> bool:
        """Check if an event is documented in the JSON."""
        events = self.json_data.get('events', {})
        
        # Check in __init__ events
        if '__init__' in events and event_name in events['__init__']:
            return True
            
        # Check in methods events
        if 'methods' in events and event_name in events['methods']:
            return True
            
        return False
    
    def generate_fix_json(self, missing: Dict[str, List[Tuple[str, Dict[str, Any]]]]) -> str:
        """Generate JSON code to fix missing events."""
        if not (missing['init_params'] or missing['methods']):
            return ""
        
        events_json = {}
        
        if missing['init_params']:
            events_json['__init__'] = {
                name: doc for name, doc in missing['init_params']
            }
        
        if missing['methods']:
            events_json['methods'] = {
                name: doc for name, doc in missing['methods']
            }
        
        # If events section doesn't exist in original JSON
        if 'events' not in self.json_data:
            return json.dumps({'events': events_json}, indent=2)
        
        # If events section exists, show only new events
        return json.dumps(events_json, indent=2)


class VerifyCommand(CommandPlugin):
    """Command for verifying component documentation."""
    
    @property
    def name(self) -> str:
        return "verify"
    
    @property
    def help(self) -> str:
        return "Verify component documentation completeness"
    
    @property
    def examples(self) -> List[str]:
        return [
            "Verify a specific component:",
            "  python -m nicegui_atlas verify upload",
            "",
            "Verify multiple components:",
            "  python -m nicegui_atlas verify button input checkbox",
            "",
            "Verify components using wildcards:",
            "  python -m nicegui_atlas verify button*",
            "",
            "Show JSON code to fix missing events:",
            "  python -m nicegui_atlas verify upload --fix"
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('components', nargs='+', help='Components to verify (supports wildcards, e.g., button*)')
        parser.add_argument('--fix', action='store_true', help='Show JSON code to fix missing events')
    
    def execute(self, args: argparse.Namespace) -> None:
        # Get component info from registry
        registry = ComponentRegistry()
        registry.initialize()
        
        # Track if any components had errors
        had_errors = False
        
        # Process each component pattern
        for pattern in args.components:
            # Convert pattern to full name if needed
            if not pattern.startswith('nicegui.'):
                if pattern.startswith('ui.'):
                    pattern = f'nicegui.{pattern}'
                else:
                    pattern = f'nicegui.ui.{pattern}'
            
            # Get all components from JSON files
            from ..component_finder import ComponentFinder
            finder = ComponentFinder()
            
            # If using wildcard, get all components
            if '*' in pattern:
                component_paths = finder.find_all()
                matching_components = []
                for path in component_paths:
                    with open(path) as f:
                        data = json.load(f)
                        if 'name' in data:
                            matching_components.append(data['name'])
            else:
                # For specific components, use the registry
                matching_components = []
                for component_name in registry.nicegui_component_index.components.keys():
                    if self._matches_pattern(component_name, pattern):
                        matching_components.append(component_name)
            
            if not matching_components:
                print(f"{Colors.RED}Error: No components found matching '{pattern}'{Colors.ENDC}")
                had_errors = True
                continue
            
            # Sort components for consistent output
            matching_components.sort()
            
            # Process each matching component
            for full_name in matching_components:
                print(f"\n{Colors.BOLD}Verifying component: {full_name}{Colors.ENDC}")
                
                # Get component info
                component_info = registry.get_nicegui_component(full_name)
                if not component_info:
                    print(f"{Colors.RED}Error: Component info not found{Colors.ENDC}")
                    had_errors = True
                    continue
                
                try:
                    self._verify_component(component_info, args.fix)
                except Exception as e:
                    print(f"{Colors.RED}Error: {str(e)}{Colors.ENDC}")
                    had_errors = True
        
        if had_errors:
            sys.exit(1)
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """Check if a component name matches a pattern with wildcards."""
        import fnmatch
        return fnmatch.fnmatch(name, pattern)
    
    def _verify_component(self, component_info: ComponentInfo, show_fix: bool) -> bool:
        """Verify a single component. Returns True if verification succeeded."""
        try:
            # Get component class from ui module (strip nicegui.ui. prefix)
            component_name = component_info.name.replace('nicegui.ui.', '')
            
            # Verify component exists in nicegui.ui
            try:
                component_class = getattr(ui, component_name)
            except AttributeError:
                print(f"{Colors.RED}Error: Component '{component_name}' does not exist in nicegui.ui module{Colors.ENDC}")
                return False
                
            # Verify component class name matches JSON name
            expected_name = f"nicegui.ui.{component_name}"
            if component_info.name != expected_name:
                print(f"{Colors.RED}Error: Component name mismatch{Colors.ENDC}")
                print(f"  JSON name: {Colors.YELLOW}{component_info.name}{Colors.ENDC}")
                print(f"  Actual name: {Colors.YELLOW}{expected_name}{Colors.ENDC}")
                return False
            
            # Create verifier with component info
            from ..component_finder import ComponentFinder
            finder = ComponentFinder()
            component_paths = finder.find_by_name(component_name)
            
            if not component_paths:
                print(f"{Colors.RED}Error: Component JSON file not found{Colors.ENDC}")
                return False
                
            verifier = ComponentVerifier(
                component_paths[0],  # Use the first matching JSON file
                component_class
            )
            info = verifier.get_component_info()
            
            # Print component overview
            print(f"\n{Colors.BOLD}{Colors.HEADER}Component: {info['name']}{Colors.ENDC}")
            if info['doc']:
                print(f"{Colors.CYAN}{info['doc']}{Colors.ENDC}\n")
            
            # Print initializer parameters
            print(f"{Colors.BOLD}Initializer Parameters:{Colors.ENDC}")
            if info['init_params']:
                for param in info['init_params']:
                    default = f" = {param['default']}" if param['default'] is not None else ""
                    print(f"  {Colors.GREEN}{param['name']}{Colors.ENDC}: {Colors.BLUE}{format_type(param['type'])}{Colors.ENDC}{Colors.YELLOW}{default}{Colors.ENDC}")
                    if param['doc']:
                        print(f"    {Colors.CYAN}{param['doc']}{Colors.ENDC}")
            else:
                print(f"  {Colors.CYAN}None{Colors.ENDC}")
            
            # Print events
            print(f"\n{Colors.BOLD}Events:{Colors.ENDC}")
            
            # Initializer Events
            print(f"\n{Colors.BOLD}  Initializer Events:{Colors.ENDC}")
            if info['events']['init']:
                for event in info['events']['init']:
                    print(f"    {Colors.YELLOW}{event['name']}{Colors.ENDC}: {Colors.BLUE}{format_type(event['type'])}{Colors.ENDC}")
                    if event['doc']:
                        print(f"      {Colors.CYAN}{event['doc']}{Colors.ENDC}")
            else:
                print(f"    {Colors.CYAN}None{Colors.ENDC}")
            
            # Method Events
            print(f"\n{Colors.BOLD}  Method Events:{Colors.ENDC}")
            if info['events']['methods']:
                for event in info['events']['methods']:
                    print(f"    {Colors.YELLOW}{event['name']}{Colors.ENDC}")
                    if event['doc']:
                        print(f"      {Colors.CYAN}{event['doc']}{Colors.ENDC}")
            else:
                print(f"    {Colors.CYAN}None{Colors.ENDC}")
            
            # Check for documentation issues
            missing = verifier.find_undocumented_events()
            orphaned = verifier.find_orphaned_events()
            
            if missing['init_params'] or missing['methods']:
                print(f"\n{Colors.BOLD}{Colors.RED}Undocumented Events:{Colors.ENDC}")
                
                if missing['init_params']:
                    print(f"\n{Colors.RED}Missing __init__ parameters:{Colors.ENDC}")
                    for param, _ in missing['init_params']:
                        print(f"  - {Colors.YELLOW}{param}{Colors.ENDC}")
                
                if missing['methods']:
                    print(f"\n{Colors.RED}Missing method events:{Colors.ENDC}")
                    for method, _ in missing['methods']:
                        print(f"  - {Colors.YELLOW}{method}{Colors.ENDC}")
                
                if show_fix:
                    print(f"\n{Colors.BOLD}JSON code to fix missing events:{Colors.ENDC}")
                    print(verifier.generate_fix_json(missing))
            
            if orphaned['init_params'] or orphaned['methods']:
                print(f"\n{Colors.BOLD}{Colors.RED}Orphaned Events (in JSON but not in Python):{Colors.ENDC}")
                
                if orphaned['init_params']:
                    print(f"\n{Colors.RED}Orphaned __init__ parameters:{Colors.ENDC}")
                    for param in orphaned['init_params']:
                        print(f"  - {Colors.YELLOW}{param}{Colors.ENDC}")
                
                if orphaned['methods']:
                    print(f"\n{Colors.RED}Orphaned method events:{Colors.ENDC}")
                    for method in orphaned['methods']:
                        print(f"  - {Colors.YELLOW}{method}{Colors.ENDC}")
            
            if not (missing['init_params'] or missing['methods'] or 
                    orphaned['init_params'] or orphaned['methods']):
                print(f"\n{Colors.GREEN}All events are properly documented.{Colors.ENDC}")
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}Error verifying component: {str(e)}{Colors.ENDC}")
            return False


# Register the plugin
command_registry.register(VerifyCommand())
