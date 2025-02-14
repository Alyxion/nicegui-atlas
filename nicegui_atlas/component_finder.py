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
        
        # Search for the component file
        paths = []
        
        # First, try exact match
        for category in self.db_path.iterdir():
            if category.is_dir() and not category.name.startswith('.'):
                json_path = category / f"{name}.json"
                if json_path.exists():
                    paths.append(str(json_path))
        
        # If no exact match, try fuzzy match
        if not paths:
            for category in self.db_path.iterdir():
                if category.is_dir() and not category.name.startswith('.'):
                    for json_path in category.glob("*.json"):
                        # Skip special files
                        if json_path.name in ['categories.json', 'template.json', 'component_mappings.json']:
                            continue
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
        
        # Handle directory filters
        if '/' in filter_str:
            dir_name, pattern = filter_str.split('/', 1)
            dir_path = self.db_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                for json_path in dir_path.glob(f"{pattern}.json"):
                    if json_path.name not in ['categories.json', 'template.json', 'component_mappings.json']:
                        paths.append(str(json_path))
        else:
            # Search in all directories
            for category in self.db_path.iterdir():
                if category.is_dir() and not category.name.startswith('.'):
                    for json_path in category.glob(f"{filter_str}.json"):
                        if json_path.name not in ['categories.json', 'template.json', 'component_mappings.json']:
                            paths.append(str(json_path))
        
        return paths
    
    def find_all(self) -> List[str]:
        """Find all component files.
        
        Returns:
            List of paths to all component files.
        """
        paths = []
        for category in self.db_path.iterdir():
            if category.is_dir() and not category.name.startswith('.'):
                for json_path in category.glob("*.json"):
                    if json_path.name not in ['categories.json', 'template.json', 'component_mappings.json']:
                        paths.append(str(json_path))
        return paths
