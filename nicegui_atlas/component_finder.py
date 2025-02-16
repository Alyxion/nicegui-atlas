"""Component finder utility for NiceGUI Atlas."""

import os
import glob
from pathlib import Path
from typing import List, Optional


class ComponentFinder:
    """Utility class for finding component files."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the component finder.
        
        Args:
            db_path: Path to the database directory. If None, uses the default db directory.
        """
        if db_path is None:
            # Go up one level from the module directory to find the db directory
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db')
        self.db_path = Path(db_path)
    
    def find_by_name(self, name: str) -> List[str]:
        """Find component files by name.
        
        Args:
            name: Component name (e.g., 'ui.button', 'button', 'btn')
            
        Returns:
            List of paths to matching component files.
        """
        # Handle different name formats
        if '.' in name:
            # Handle ui.button format
            name = name.split('.')[-1]
        
        # Load component mappings
        mappings_file = self.db_path / "component_mappings.json"
        if mappings_file.exists():
            import json
            with open(mappings_file) as f:
                mappings = json.load(f)
                url_mappings = mappings.get("url_mappings", {})
                # Check if name is in mappings
                if name in url_mappings:
                    name = url_mappings[name]
        
        # Search for the component file in the components directory
        paths = []
        components_dir = self.db_path / "components"
        
        # First, try exact match
        json_path = components_dir / f"{name}.json"
        if json_path.exists():
            paths.append(str(json_path))
        
        # If no exact match, try fuzzy match
        if not paths:
            for json_path in components_dir.glob("*.json"):
                # Check if component name is part of the file name
                if name.lower() in json_path.stem.lower():
                    paths.append(str(json_path))
        
        return paths
    
    def find_by_filter(self, filter_str: str) -> List[str]:
        """Find component files by filter string.
        
        Args:
            filter_str: Filter string (e.g., 'basic', 'input/*', 'button*')
            
        Returns:
            List of paths to matching component files.
        """
        paths = []
        
        # Search in components directory
        components_dir = self.db_path / "components"
        for json_path in components_dir.glob(f"{filter_str}.json"):
            paths.append(str(json_path))
        
        return paths
    
    def find_all(self) -> List[str]:
        """Find all component files.
        
        Returns:
            List of paths to all component files.
        """
        components_dir = self.db_path / "components"
        paths = [str(p) for p in components_dir.glob("*.json")]
        return paths
