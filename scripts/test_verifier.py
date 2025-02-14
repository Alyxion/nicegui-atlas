"""Test the new Quasar verifier implementation."""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import nicegui_atlas
sys.path.append(str(Path(__file__).parent.parent))

from nicegui_atlas.quasar_verifier import verify_component_sync

def main():
    """Test the verifier with the button component."""
    button_file = Path(__file__).parent.parent / "db" / "basic_elements" / "button.json"
    
    print("Testing button component verification...")
    issues = verify_component_sync(str(button_file))
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("\nNo issues found!")

if __name__ == "__main__":
    main()
