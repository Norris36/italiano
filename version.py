"""
Version management for Italian Dictionary project
~~~
- Semantic versioning (MAJOR.MINOR.PATCH)
- Automatic version incrementing
- Version history tracking
- Integration with dictionary updates
~~~
returns: Version utilities and constants
"""

from datetime import datetime
from typing import Dict, List, Tuple
import json

# Current version
MAJOR = 1
MINOR = 0  
PATCH = 0

VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
VERSION_DATE = "2025-09-04"
VERSION_DESCRIPTION = "Initial release with core dictionary functionality"

class VersionManager:
    """
    Manages version tracking for the Italian dictionary
    ~~~
    - Track version history in separate file
    - Automatic version bumping
    - Changelog generation
    - Integration with dictionary updates
    ~~~
    returns: VersionManager instance
    """
    
    def __init__(self, version_file: str = "version_history.json"):
        """
        Initialize version manager
        ~~~
        - Load existing version history
        - Set current version info
        ~~~
        returns: None
        """
        self.version_file = version_file
        self.history = self._load_version_history()
        
    def _load_version_history(self) -> List[Dict]:
        """
        Load version history from JSON file
        ~~~
        - Create file if doesn't exist
        - Load existing history
        ~~~
        returns: List of version entries
        """
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create initial version entry
            initial_version = {
                "version": VERSION,
                "date": VERSION_DATE,
                "description": VERSION_DESCRIPTION,
                "changes": [
                    "Initial dictionary structure with 20 essential words",
                    "Verb conjugation system implemented", 
                    "English-Italian bidirectional search",
                    "CSV export functionality",
                    "GitHub raw URL integration"
                ],
                "word_count": 20,
                "new_features": [
                    "Dictionary JSON schema",
                    "Python dictionary manager class",
                    "Jupyter notebook interface",
                    "Backup and export functions"
                ]
            }
            return [initial_version]
    
    def save_version_history(self) -> None:
        """
        Save version history to JSON file
        ~~~
        - Write formatted JSON with version data
        ~~~
        returns: None
        """
        with open(self.version_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def get_current_version(self) -> str:
        """
        Get current version string
        ~~~
        - Return semantic version format
        ~~~
        returns: str with current version
        """
        return VERSION
    
    def get_version_info(self) -> Dict:
        """
        Get detailed current version information
        ~~~
        - Return version with metadata
        ~~~
        returns: Dict with version details
        """
        return {
            "version": VERSION,
            "date": VERSION_DATE, 
            "description": VERSION_DESCRIPTION,
            "major": MAJOR,
            "minor": MINOR,
            "patch": PATCH
        }
    
    def increment_patch(self, description: str, changes: List[str] = None) -> str:
        """
        Increment patch version (bug fixes)
        ~~~
        - Bump patch number
        - Add changelog entry
        - Update version constants
        ~~~
        returns: str with new version
        """
        return self._increment_version('patch', description, changes or [])
    
    def increment_minor(self, description: str, changes: List[str] = None) -> str:
        """
        Increment minor version (new features)
        ~~~
        - Bump minor number, reset patch
        - Add changelog entry
        - Update version constants  
        ~~~
        returns: str with new version
        """
        return self._increment_version('minor', description, changes or [])
    
    def increment_major(self, description: str, changes: List[str] = None) -> str:
        """
        Increment major version (breaking changes)
        ~~~
        - Bump major number, reset minor and patch
        - Add changelog entry
        - Update version constants
        ~~~
        returns: str with new version
        """
        return self._increment_version('major', description, changes or [])
    
    def _increment_version(self, level: str, description: str, changes: List[str]) -> str:
        """
        Internal method to increment version
        ~~~
        - Update version numbers based on level
        - Create new history entry
        - Save to file
        ~~~
        returns: str with new version
        """
        global MAJOR, MINOR, PATCH, VERSION, VERSION_DATE, VERSION_DESCRIPTION
        
        # Increment version numbers
        if level == 'major':
            MAJOR += 1
            MINOR = 0
            PATCH = 0
        elif level == 'minor':
            MINOR += 1
            PATCH = 0
        elif level == 'patch':
            PATCH += 1
        
        # Update global constants
        VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
        VERSION_DATE = datetime.now().strftime("%Y-%m-%d")
        VERSION_DESCRIPTION = description
        
        # Create new history entry
        new_entry = {
            "version": VERSION,
            "date": VERSION_DATE,
            "description": description,
            "changes": changes,
            "increment_type": level
        }
        
        self.history.append(new_entry)
        self.save_version_history()
        
        return VERSION
    
    def get_changelog(self, limit: int = None) -> List[Dict]:
        """
        Get version changelog
        ~~~
        - Return recent version history
        - Optionally limit number of entries
        ~~~
        returns: List of changelog entries
        """
        if limit:
            return self.history[-limit:]
        return self.history
    
    def generate_changelog_markdown(self) -> str:
        """
        Generate markdown changelog
        ~~~
        - Format version history as markdown
        - Include dates, changes, and descriptions
        ~~~
        returns: str with markdown changelog
        """
        lines = ["# Changelog\n"]
        
        for entry in reversed(self.history):
            lines.append(f"## Version {entry['version']} - {entry['date']}\n")
            lines.append(f"{entry['description']}\n")
            
            if entry.get('changes'):
                lines.append("### Changes")
                for change in entry['changes']:
                    lines.append(f"- {change}")
                lines.append("")
            
            if entry.get('new_features'):
                lines.append("### New Features")
                for feature in entry['new_features']:
                    lines.append(f"- {feature}")
                lines.append("")
            
            lines.append("---\n")
        
        return "\n".join(lines)

def get_version() -> str:
    """
    Simple function to get current version
    ~~~
    - Return version string for imports
    ~~~
    returns: str with current version
    """
    return VERSION

def update_dictionary_version(dictionary_data: Dict, version_manager: VersionManager) -> Dict:
    """
    Update dictionary metadata with current version
    ~~~
    - Set version in dictionary metadata
    - Update last_updated timestamp
    ~~~
    returns: Dict with updated dictionary
    """
    if 'metadata' not in dictionary_data:
        dictionary_data['metadata'] = {}
    
    dictionary_data['metadata']['version'] = version_manager.get_current_version()
    dictionary_data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    return dictionary_data