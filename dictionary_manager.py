import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union
import pandas as pd
from version import VersionManager, update_dictionary_version

class ItalianDictionary:
    """
    Manages English-Italian dictionary with verb conjugations
    ~~~
    - Load dictionary from local JSON or GitHub raw URL
    - Search for translations with multiple matches
    - Add new words with conjugations
    - Export to various formats
    - Update version and metadata
    ~~~
    returns: ItalianDictionary instance
    """
    
    def __init__(self, source: str = "dictionary.json"):
        """
        Initialize dictionary manager
        ~~~
        - Load from local file or GitHub URL
        - Validate dictionary structure
        - Set up internal data structures
        - Initialize version manager
        ~~~
        returns: None
        """
        self.source = source
        self.data = {}
        self.version_manager = VersionManager()
        self.load_dictionary()
    
    def load_dictionary(self) -> None:
        """
        Load dictionary from source
        ~~~
        - Check if source is URL or local file
        - Load and parse JSON data
        - Validate required structure
        ~~~
        returns: None
        """
        try:
            if self.source.startswith(('http://', 'https://')):
                response = requests.get(self.source)
                response.raise_for_status()
                self.data = response.json()
            else:
                with open(self.source, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            
            # Validate structure
            if 'words' not in self.data:
                raise ValueError("Dictionary must have 'words' key")
            if 'metadata' not in self.data:
                self.data['metadata'] = self._create_default_metadata()
                
        except (FileNotFoundError, requests.RequestException, json.JSONDecodeError) as e:
            print(f"Error loading dictionary: {e}")
            self.data = self._create_empty_dictionary()
    
    def _create_default_metadata(self) -> Dict:
        """
        Create default metadata structure
        ~~~
        - Set version, timestamp, word count
        - Add description
        ~~~
        returns: Dict with metadata
        """
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_words": len(self.data.get('words', {})),
            "description": "English-Italian dictionary with verb conjugations"
        }
    
    def _create_empty_dictionary(self) -> Dict:
        """
        Create empty dictionary structure
        ~~~
        - Initialize with metadata and empty words
        ~~~
        returns: Dict with empty dictionary structure
        """
        return {
            "metadata": self._create_default_metadata(),
            "words": {}
        }
    
    def search_word(self, english_word: str) -> Optional[Dict]:
        """
        Search for English word in dictionary
        ~~~
        - Find exact match for English word
        - Return word data with translations and conjugations
        ~~~
        returns: Dict with word data or None if not found
        """
        return self.data['words'].get(english_word.lower())
    
    def search_translations(self, english_word: str) -> List[str]:
        """
        Get all Italian translations for English word
        ~~~
        - Find word entry
        - Extract all translations
        ~~~
        returns: List of Italian translations
        """
        word_data = self.search_word(english_word)
        if word_data:
            return word_data.get('translations', [])
        return []
    
    def search_by_italian(self, italian_word: str) -> List[str]:
        """
        Find English words that translate to given Italian word
        ~~~
        - Search through all translations
        - Return matching English words
        ~~~
        returns: List of English words
        """
        matches = []
        italian_lower = italian_word.lower()
        
        for english_word, word_data in self.data['words'].items():
            translations = word_data.get('translations', [])
            if any(italian_lower == trans.lower() for trans in translations):
                matches.append(english_word)
        
        return matches
    
    def get_conjugations(self, english_word: str, italian_verb: str = None) -> Optional[Dict]:
        """
        Get verb conjugations for English word
        ~~~
        - Find word entry and conjugations
        - Return specific verb conjugations or all
        ~~~
        returns: Dict with conjugations or None
        """
        word_data = self.search_word(english_word)
        if not word_data or word_data.get('type') != 'verb':
            return None
        
        conjugations = word_data.get('conjugations', {})
        
        if italian_verb:
            return conjugations.get(italian_verb)
        
        return conjugations
    
    def add_word(self, english_word: str, word_type: str, translations: List[str], 
                 conjugations: Dict = None, **kwargs) -> None:
        """
        Add new word to dictionary
        ~~~
        - Create word entry with type and translations
        - Add conjugations for verbs
        - Update metadata
        ~~~
        returns: None
        """
        word_entry = {
            "type": word_type,
            "translations": translations,
            "frequency_rank": kwargs.get('frequency_rank', 999),
            "category": kwargs.get('category', 'user_added')
        }
        
        # Add optional fields
        if conjugations and word_type == 'verb':
            word_entry["conjugations"] = conjugations
        
        if 'gender' in kwargs:
            word_entry["gender"] = kwargs['gender']
            
        if 'notes' in kwargs:
            word_entry["notes"] = kwargs['notes']
        
        self.data['words'][english_word.lower()] = word_entry
        self._update_metadata()
    
    def add_verb_conjugations(self, english_verb: str, italian_verb: str, 
                             tense: str, conjugations: Dict[str, str]) -> None:
        """
        Add conjugations for specific verb and tense
        ~~~
        - Find existing verb entry
        - Add or update conjugation data
        - Update metadata
        ~~~
        returns: None
        """
        word_data = self.search_word(english_verb)
        if not word_data:
            raise ValueError(f"Word '{english_verb}' not found in dictionary")
        
        if word_data.get('type') != 'verb':
            raise ValueError(f"Word '{english_verb}' is not a verb")
        
        if 'conjugations' not in word_data:
            word_data['conjugations'] = {}
        
        if italian_verb not in word_data['conjugations']:
            word_data['conjugations'][italian_verb] = {}
        
        word_data['conjugations'][italian_verb][tense] = conjugations
        self._update_metadata()
    
    def get_words_by_category(self, category: str) -> List[str]:
        """
        Get all words in specific category
        ~~~
        - Filter words by category
        - Return list of English words
        ~~~
        returns: List of English words in category
        """
        return [
            word for word, data in self.data['words'].items()
            if data.get('category') == category
        ]
    
    def get_most_frequent_words(self, limit: int = 50) -> List[str]:
        """
        Get most frequent words by rank
        ~~~
        - Sort words by frequency rank
        - Return top N words
        ~~~
        returns: List of English words sorted by frequency
        """
        words_with_rank = [
            (word, data.get('frequency_rank', 999)) 
            for word, data in self.data['words'].items()
        ]
        
        words_with_rank.sort(key=lambda x: x[1])
        return [word for word, rank in words_with_rank[:limit]]
    
    def export_to_csv(self, filename: str = "italian_dictionary.csv") -> None:
        """
        Export dictionary to CSV format
        ~~~
        - Flatten word data for CSV export
        - Include translations and basic info
        ~~~
        returns: None
        """
        rows = []
        for english_word, word_data in self.data['words'].items():
            for translation in word_data.get('translations', []):
                rows.append({
                    'english': english_word,
                    'italian': translation,
                    'type': word_data.get('type', ''),
                    'category': word_data.get('category', ''),
                    'frequency_rank': word_data.get('frequency_rank', 999),
                    'gender': word_data.get('gender', ''),
                    'notes': word_data.get('notes', '')
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Dictionary exported to {filename}")
    
    def export_conjugations_csv(self, filename: str = "italian_conjugations.csv") -> None:
        """
        Export verb conjugations to CSV format
        ~~~
        - Extract all conjugation data
        - Create flat CSV structure
        ~~~
        returns: None
        """
        rows = []
        for english_verb, word_data in self.data['words'].items():
            if word_data.get('type') == 'verb' and 'conjugations' in word_data:
                for italian_verb, tenses in word_data['conjugations'].items():
                    for tense, persons in tenses.items():
                        for person, conjugated in persons.items():
                            rows.append({
                                'english_verb': english_verb,
                                'italian_verb': italian_verb,
                                'tense': tense,
                                'person': person,
                                'conjugated_form': conjugated
                            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Conjugations exported to {filename}")
    
    def save_dictionary(self, filename: str = None) -> None:
        """
        Save dictionary to JSON file
        ~~~
        - Update metadata with version info before saving
        - Write formatted JSON to file
        ~~~
        returns: None
        """
        if filename is None:
            filename = self.source if not self.source.startswith('http') else "dictionary.json"
        
        self._update_metadata()
        self.data = update_dictionary_version(self.data, self.version_manager)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        print(f"Dictionary saved to {filename}")
    
    def _update_metadata(self) -> None:
        """
        Update metadata with current stats
        ~~~
        - Update word count and timestamp
        - Increment version if needed
        ~~~
        returns: None
        """
        self.data['metadata']['total_words'] = len(self.data['words'])
        self.data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    
    def get_stats(self) -> Dict:
        """
        Get dictionary statistics
        ~~~
        - Count words by type and category
        - Return comprehensive stats
        ~~~
        returns: Dict with statistics
        """
        stats = {
            'total_words': len(self.data['words']),
            'by_type': {},
            'by_category': {},
            'verbs_with_conjugations': 0
        }
        
        for word_data in self.data['words'].values():
            word_type = word_data.get('type', 'unknown')
            category = word_data.get('category', 'unknown')
            
            stats['by_type'][word_type] = stats['by_type'].get(word_type, 0) + 1
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            if word_type == 'verb' and 'conjugations' in word_data:
                stats['verbs_with_conjugations'] += 1
        
        return stats

def create_github_url(username: str, repo: str, filename: str = "dictionary.json", branch: str = "dev") -> str:
    """
    Create GitHub raw URL for dictionary access
    ~~~
    - Build raw.githubusercontent.com URL
    - Use dev branch by default
    ~~~
    returns: str with GitHub raw URL
    """
    return f"https://raw.githubusercontent.com/{username}/{repo}/{branch}/{filename}"

# Example usage and testing functions
def main():
    """
    Demonstrate dictionary functionality
    ~~~
    - Create dictionary instance
    - Show search and add operations
    - Display statistics
    ~~~
    returns: None
    """
    # Initialize dictionary
    dictionary = ItalianDictionary("dictionary.json")
    
    # Show stats
    print("Dictionary Statistics:")
    stats = dictionary.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Search examples
    print("\nSearch Examples:")
    word = "be"
    translations = dictionary.search_translations(word)
    print(f"'{word}' -> {translations}")
    
    conjugations = dictionary.get_conjugations(word, "essere")
    if conjugations:
        print(f"Conjugations for 'essere':")
        for tense, persons in conjugations.items():
            print(f"  {tense}: {persons}")
    
    # Search by Italian
    italian_matches = dictionary.search_by_italian("ciao")
    print(f"Words that translate to 'ciao': {italian_matches}")

if __name__ == "__main__":
    main()