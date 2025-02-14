"""Component information formatters."""

from typing import List, Optional

from .models import ComponentInfo, Example


def format_examples(examples: List[Example], indent: int = 0) -> str:
    """Format examples with proper indentation."""
    if not examples:
        return ""
    
    lines = ["Examples:"]
    for example in examples:
        lines.append(example.code)
        if example.description:
            lines.append(f"# {example.description}")
    
    return "\n".join(" " * indent + line for line in lines)


def format_property(name: str, prop, indent: int = 2) -> List[str]:
    """Format a property's information."""
    lines = []
    type_str = f"({prop.type})" if prop.type else ""
    desc = f": {prop.description}" if prop.description else ""
    
    if prop.default is not None:
        desc = f"{desc} (default: {prop.default})"
    
    lines.append(f"{' ' * indent}{name} {type_str}{desc}")
    
    if prop.examples:
        example_text = format_examples(prop.examples, indent + 2)
        if example_text:
            lines.append(example_text)
    
    return lines


def format_argument(arg, indent: int = 6) -> List[str]:
    """Format an argument's information."""
    lines = []
    type_str = f"({arg.type})" if arg.type else ""
    desc = f": {arg.description}" if arg.description else ""
    
    if arg.default is not None:
        desc = f"{desc} (default: {arg.default})"
    
    lines.append(f"{' ' * indent}{arg.name} {type_str}{desc}")
    
    if arg.examples:
        example_text = format_examples(arg.examples, indent + 2)
        if example_text:
            lines.append(example_text)
    
    return lines


def format_event(name: str, event, indent: int = 2) -> List[str]:
    """Format an event's information."""
    lines = []
    desc = f": {event.description}" if event.description else ""
    lines.append(f"{' ' * indent}{name}{desc}")
    
    if event.arguments:
        lines.append(f"{' ' * (indent + 2)}Arguments:")
        for arg in event.arguments:
            lines.extend(format_argument(arg))
    
    if event.examples:
        example_text = format_examples(event.examples, indent + 2)
        if example_text:
            lines.append(example_text)
    
    return lines


def format_function(name: str, func, indent: int = 2) -> List[str]:
    """Format a function's information."""
    lines = []
    return_str = f" -> {func.return_type}" if func.return_type else ""
    desc = f": {func.description}" if func.description else ""
    lines.append(f"{' ' * indent}{name}{return_str}{desc}")
    
    if func.arguments:
        lines.append(f"{' ' * (indent + 2)}Arguments:")
        for arg in func.arguments:
            lines.extend(format_argument(arg))
    
    if func.examples:
        example_text = format_examples(func.examples, indent + 2)
        if example_text:
            lines.append(example_text)
    
    return lines


def format_tech_info(component: ComponentInfo) -> str:
    """Format technical information about a component."""
    tech_parts = []
    
    if component.direct_ancestors:
        tech_parts.append(f"Python: {', '.join(component.direct_ancestors)}")
    
    if component.quasar_components:
        quasar_names = []
        for qc in component.quasar_components:
            if isinstance(qc, str):
                quasar_names.append(qc)
            else:
                quasar_names.append(qc.name)
        tech_parts.append(f"Quasar: {', '.join(quasar_names)}")
    
    if component.libraries:
        tech_parts.append(f"Library: {', '.join(lib.name for lib in component.libraries)}")
    
    if component.internal_components:
        tech_parts.append(f"Internal: {', '.join(component.internal_components)}")
    
    if component.html_element:
        tech_parts.append(f"HTML: {component.html_element}")
    
    return " | ".join(tech_parts)


def format_component(component: ComponentInfo, sections: Optional[List[str]] = None) -> str:
    """Format component information for display.
    
    Args:
        component: The component to format
        sections: Optional list of sections to include ('properties', 'events', 'functions')
                 If None, includes all sections
    """
    lines = [f"\n=== {component.name} ==="]
    
    if component.doc_url:
        lines.append(f"Documentation: {component.doc_url}\n")
    
    if component.description:
        lines.append(f"{component.description}\n")
    
    # For NiceGUI components, show technical info
    if component.type == "nicegui":
        tech_info = format_tech_info(component)
        if tech_info:
            lines.append(f"Technical Info: {tech_info}\n")
    
    if not sections or "properties" in sections:
        if component.properties:
            lines.append("Properties:")
            for name, prop in sorted(component.properties.items()):
                lines.extend(format_property(name, prop))
            lines.append("")
    
    if not sections or "events" in sections:
        if component.events:
            lines.append("Events:")
            for name, event in sorted(component.events.items()):
                lines.extend(format_event(name, event))
            lines.append("")
    
    if not sections or "functions" in sections:
        if component.functions:
            lines.append("Functions:")
            for name, func in sorted(component.functions.items()):
                lines.extend(format_function(name, func))
            lines.append("")
    
    if component.examples:
        lines.append("Examples:")
        for example in component.examples:
            lines.append(example.code)
            if example.description:
                lines.append(f"# {example.description}")
        lines.append("")
    
    return "\n".join(lines)
