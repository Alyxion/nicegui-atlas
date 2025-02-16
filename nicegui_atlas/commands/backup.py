"""Backup command to create copies of NiceGUI component files."""

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..commands.base import CommandPlugin, registry


class Backup:
    """Class to handle NiceGUI component backups."""
    
    def __init__(self, nicegui_path: Optional[str] = None, output_dir: str = 'backups'):
        """Initialize the backup handler.
        
        Args:
            nicegui_path: Path to NiceGUI package. If None, will try to get from env.
            output_dir: Directory to store backups in.
        """
        self.nicegui_path = nicegui_path or os.getenv('NICEGUI_PATH')
        if not self.nicegui_path:
            raise ValueError("NICEGUI_PATH not set")
        
        # Add nicegui package path
        self.nicegui_path = str(Path(self.nicegui_path) / 'nicegui')
        self.output_dir = output_dir
        
    def calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def get_referenced_files(self) -> Set[str]:
        """Get set of files referenced in JSON files."""
        referenced_files = set()
        db_dir = Path('db')
        
        for subdir in db_dir.iterdir():
            if subdir.is_dir():
                for json_file in subdir.glob('*.json'):
                    try:
                        with open(json_file) as f:
                            component_data = json.load(f)
                            source_path = component_data.get('source_path')
                            if source_path and not source_path.startswith('$'):
                                # Add Python file
                                referenced_files.add(Path(source_path).name)
                                # Add potential JS file
                                referenced_files.add(Path(source_path).stem + '.js')
                    except Exception as e:
                        print(f"Error reading {json_file}: {str(e)}")
        
        return referenced_files
    
    def backup_component(self, json_path: Path, component_data: Dict, referenced_files: Set[str]) -> Dict:
        """Backup a single component and update its metadata.
        
        Args:
            json_path: Path to the component's JSON file
            component_data: The component's JSON data
            referenced_files: Set of files referenced in JSONs
            
        Returns:
            Updated component data with checksums
        """
        source_path = component_data.get('source_path')
        if not source_path or source_path.startswith('$'):
            return component_data
        
        # Create backup directories
        backup_dir = Path(self.output_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        updated_data = component_data.copy()
        
        # Only backup files that are referenced
        py_name = Path(source_path).name
        js_name = Path(source_path).stem + '.js'
        
        if py_name in referenced_files:
            # Backup Python file
            py_src = Path(self.nicegui_path) / 'elements' / py_name
            if py_src.exists():
                py_dest = backup_dir / source_path
                py_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(py_src, py_dest)
                print(f"Backed up Python file: {source_path}")
                updated_data['py_checksum'] = self.calculate_md5(py_src)
        
        if js_name in referenced_files:
            # Backup component-specific JS file
            js_src = Path(self.nicegui_path) / 'elements' / js_name
            if js_src.exists():
                js_rel_path = f'elements/{js_name}'
                js_dest = backup_dir / js_rel_path
                js_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(js_src, js_dest)
                print(f"Backed up JavaScript file: {js_rel_path}")
                updated_data['js_checksum'] = self.calculate_md5(js_src)

            # Backup library JS files only if component JS exists
            lib_dir = Path(self.nicegui_path) / 'elements' / 'lib' / Path(source_path).stem
            if lib_dir.exists():
                lib_checksums = []
                for js_file in lib_dir.rglob('*.js'):
                    lib_rel_path = js_file.relative_to(Path(self.nicegui_path))
                    lib_dest = backup_dir / lib_rel_path
                    lib_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(js_file, lib_dest)
                    print(f"Backed up library file: {lib_rel_path}")
                    lib_checksums.append({
                        'path': str(lib_rel_path),
                        'checksum': self.calculate_md5(js_file)
                    })
                if lib_checksums:
                    updated_data['lib_checksums'] = lib_checksums
        
        return updated_data
    
    def clean_backup_dir(self) -> None:
        """Clean the backup directory and its subdirectories."""
        backup_dir = Path(self.output_dir)
        if backup_dir.exists():
            # Remove all contents but keep the directory
            for item in backup_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print("Cleared old backups")
    
    def backup_all(self, clean: bool = False) -> None:
        """Backup all components and update their metadata.
        
        Args:
            clean: If True, remove existing backups before creating new ones.
        """
        if clean:
            self.clean_backup_dir()
        
        # Get all referenced files first
        referenced_files = self.get_referenced_files()
        
        # Get all JSON files from db directory
        db_dir = Path('db')
        json_files = []
        for subdir in db_dir.iterdir():
            if subdir.is_dir():
                json_files.extend(subdir.glob('*.json'))
        
        # Process each component
        for json_file in json_files:
            try:
                with open(json_file) as f:
                    component_data = json.load(f)
                
                # Backup files and update metadata
                updated_data = self.backup_component(json_file, component_data, referenced_files)
                
                # Write updated JSON back to file
                with open(json_file, 'w') as f:
                    json.dump(updated_data, f, indent=2)
                
            except Exception as e:
                print(f"Error processing {json_file}: {str(e)}")
        
        print(f"\nBackup completed. Files saved to: {self.output_dir}")


class BackupCommand(CommandPlugin):
    """Command to backup NiceGUI component files."""
    
    @property
    def name(self) -> str:
        return "backup"
    
    @property
    def help(self) -> str:
        return "Create backups of NiceGUI component files"
    
    @property
    def examples(self) -> List[str]:
        return [
            "atlas backup  # Create backups of all component files",
            "atlas backup --clean  # Clear old backups before creating new ones",
            "atlas backup --output-dir path/to/dir  # Specify backup directory"
        ]
    
    def setup_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--output-dir',
            help='Output directory for backups (default: ./backups)',
            default='backups'
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clear old backups before creating new ones'
        )
    
    def execute(self, args: argparse.Namespace) -> None:
        """Execute the backup command."""
        # Load environment variables from .env
        try:
            with open('.env') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                        print(f"Loaded {key}={value}")
        except Exception as e:
            print(f"Error loading .env file: {str(e)}")
            return

        try:
            backup = Backup(output_dir=args.output_dir)
            backup.backup_all(clean=args.clean)
        except Exception as e:
            print(f"Error during backup: {str(e)}")


# Register the command
registry.register(BackupCommand())
