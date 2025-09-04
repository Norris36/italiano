# Italian Dictionary Project 🇮🇹

A comprehensive English-Italian dictionary system with verb conjugations, built following the Pareto principle to focus on the most essential words first.

## ⚠️ Disclaimer

**Translation Accuracy**: The translations in this dictionary are not 100% accurate and are continuously being updated and refined as I learn. This is a personal learning project, and while I strive for accuracy, please verify important translations with authoritative sources.

## 🎯 Project Goals

- Build a practical English-Italian dictionary starting with 100 essential words
- Expand iteratively to reach 1000 words following the Pareto principle (80/20 rule)
- Focus on high-frequency words that cover the majority of everyday communication
- Include comprehensive verb conjugations for different tenses
- Create an accessible system that works both locally and via GitHub

## 📁 Project Structure

```
italian/
├── README.md                    # This file
├── dictionary.json              # Main dictionary database
├── dictionary_manager.py        # Python class for managing dictionary
├── version.py                   # Version management system
├── version_history.json         # Version changelog (auto-generated)
├── pdf_creator.py              # PDF quiz generator
├── main.ipynb                  # Jupyter notebook for development/testing
└── exports/                    # Generated CSV exports (optional)
    ├── italian_words.csv
    └── italian_conjugations.csv
```

## 🚀 Features

### Core Dictionary Features
- **Bidirectional Search**: English → Italian and Italian → English
- **Multiple Translations**: Words can have multiple translations (e.g., "know" → ["sapere", "conoscere"])
- **Verb Conjugations**: Complete conjugation tables for Italian verbs across different tenses
- **Word Categories**: Organized by categories (essential, greetings, basic_needs, etc.)
- **Frequency Ranking**: Words ranked by usage frequency following Pareto principle
- **Gender Information**: Noun gender tracking (masculine/feminine)
- **Usage Notes**: Additional context for translations (e.g., when to use "sapere" vs "conoscere")

### Technical Features
- **JSON Database**: Structured, human-readable format
- **GitHub Integration**: Access via raw GitHub URLs from anywhere
- **Version Control**: Semantic versioning with automatic changelog generation  
- **Export Options**: CSV export for external use
- **Jupyter Integration**: Notebook-based development and testing
- **Backup System**: Automatic backup creation

## 🛠️ Installation & Setup

### Prerequisites
```bash
pip install pandas requests
```

### Basic Usage
```python
# Import the dictionary manager
from dictionary_manager import ItalianDictionary

# Initialize dictionary
dict_manager = ItalianDictionary("dictionary.json")

# Search for translations
translations = dict_manager.search_translations("hello")
print(f"hello → {translations}")  # ['ciao', 'salve']

# Get verb conjugations
conjugations = dict_manager.get_conjugations("be", "essere")
print(conjugations["presente"])  # {'io': 'sono', 'tu': 'sei', ...}
```

### Notebook Development
Open `main.ipynb` for interactive development and testing. The notebook includes:
- Dictionary statistics and exploration
- Helper functions for adding new words
- Search and display functions
- Backup and export utilities

## 📖 Dictionary Schema

### Word Entry Structure
```json
{
  "word": {
    "type": "verb|noun|adjective|phrase|adverb",
    "translations": ["italian_word1", "italian_word2"],
    "conjugations": {  // Only for verbs
      "italian_verb": {
        "presente": {"io": "form", "tu": "form", ...},
        "passato_prossimo": {"io": "form", "tu": "form", ...}
      }
    },
    "frequency_rank": 1,
    "category": "essential|greetings|basic_needs|...",
    "gender": "masculine|feminine",  // For nouns
    "notes": "Additional context or usage notes"
  }
}
```

### Supported Verb Tenses
- **presente** (present): io, tu, lui/lei, noi, voi, loro
- **passato_prossimo** (present perfect): with auxiliary verbs
- **imperfetto** (imperfect): past continuous/habitual
- **futuro** (future): will forms
- **condizionale** (conditional): would forms
- **congiuntivo** (subjunctive): doubt/emotion/opinion

## 🔧 API Reference

### ItalianDictionary Class

#### Core Methods
```python
# Search and lookup
search_word(english_word) -> Dict           # Get complete word entry
search_translations(english_word) -> List  # Get Italian translations
search_by_italian(italian_word) -> List    # Find English words for Italian
get_conjugations(verb, italian_verb) -> Dict  # Get verb conjugations

# Adding content
add_word(english, type, translations, **kwargs)  # Add new word
add_verb_conjugations(verb, italian_verb, tense, conjugations)  # Add conjugations

# Organization
get_words_by_category(category) -> List     # Filter by category
get_most_frequent_words(limit) -> List     # Get high-frequency words
get_stats() -> Dict                        # Dictionary statistics

# Export and backup
save_dictionary(filename)                   # Save to JSON
export_to_csv(filename)                    # Export words to CSV
export_conjugations_csv(filename)          # Export conjugations to CSV
```

#### Helper Functions (in notebook)
```python
# Easy word addition
add_simple_word("cat", ["gatto"], "noun", "animals", gender="masculine")

# Verb with conjugations
add_verb_with_conjugations("eat", "mangiare", {
    "io": "mangio", "tu": "mangi", "lui/lei": "mangia",
    "noi": "mangiamo", "voi": "mangiate", "loro": "mangiano"
})

# Search and display
search_and_display("know")  # Shows all translations and conjugations
```

## 🌐 GitHub Integration

### Access Dictionary from Anywhere
```python
# Use raw GitHub URL
github_url = "https://raw.githubusercontent.com/Norris36/italiano/dev/dictionary.json"
dict_remote = ItalianDictionary(github_url)

# Now you can use the dictionary from any Python environment
translations = dict_remote.search_translations("water")
```

### Development Workflow
1. **Development**: Work on `dev` branch
2. **Testing**: Merge to `test` branch for validation
3. **Production**: Create pull request to `master` when ready

## 📊 Version Management

The project uses semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to dictionary structure
- **MINOR**: New features (new word categories, functionality)
- **PATCH**: Bug fixes, translation corrections, small additions

### Version History
Check `version_history.json` for detailed changelog or use:
```python
from version import VersionManager
vm = VersionManager()
print(vm.generate_changelog_markdown())
```

## 📈 Current Statistics

- **Total Words**: 20 (goal: 1000)
- **Verbs with Conjugations**: 7
- **Categories**: 8 (essential, greetings, basic_needs, time, places, etc.)
- **Most Recent Version**: v1.0.0

## 🎯 Learning Approach

This dictionary follows the **Pareto Principle (80/20 rule)**:

1. **Phase 1 (Current)**: 100 most essential words covering ~80% of basic communication
2. **Phase 2**: Expand to 300 words for ~90% coverage  
3. **Phase 3**: Reach 1000 words for comprehensive everyday Italian

### Word Priority Categories
1. **Essential verbs**: be, have, go, do, say, see, know
2. **Greetings & Politeness**: hello, goodbye, thank you, please
3. **Basic needs**: water, food, house, money, time
4. **Common adjectives**: good, bad, big, small, new, old
5. **Numbers**: 1-100, ordinals
6. **Time expressions**: day, night, today, tomorrow
7. **Family & people**: family, friend, person, man, woman
8. **Actions**: eat, drink, sleep, work, study, travel

## 🤝 Contributing

This is a personal learning project, but suggestions are welcome:

1. **Translation corrections**: Submit issues with corrections
2. **New word suggestions**: Propose high-frequency words to add
3. **Feature requests**: Suggest improvements to the system

## 📝 Usage Examples

### Basic Dictionary Lookup
```python
# Initialize
dict_manager = ItalianDictionary()

# Simple translation
dict_manager.search_translations("water")  # ['acqua']

# Multiple translations
dict_manager.search_translations("know")   # ['sapere', 'conoscere']

# Reverse lookup
dict_manager.search_by_italian("ciao")     # ['hello', 'goodbye']
```

### Working with Verbs
```python
# Get all conjugations for "essere" (to be)
conjugations = dict_manager.get_conjugations("be", "essere")

# Present tense
print(conjugations["presente"])
# Output: {'io': 'sono', 'tu': 'sei', 'lui/lei': 'è', 'noi': 'siamo', 'voi': 'siete', 'loro': 'sono'}

# Past perfect
print(conjugations["passato_prossimo"]) 
# Output: {'io': 'sono stato/a', 'tu': 'sei stato/a', ...}
```

### Adding New Content
```python
# Add a simple noun
dict_manager.add_word("cat", "noun", ["gatto"], 
                     frequency_rank=150, category="animals", gender="masculine")

# Add a verb with conjugations
presente_mangiare = {
    "io": "mangio", "tu": "mangi", "lui/lei": "mangia",
    "noi": "mangiamo", "voi": "mangiate", "loro": "mangiano"
}

dict_manager.add_word("eat", "verb", ["mangiare"], 
                     conjugations={"mangiare": {"presente": presente_mangiare}})

# Save changes
dict_manager.save_dictionary()
```

### Export and Backup
```python
# Create CSV exports
dict_manager.export_to_csv("my_italian_words.csv")
dict_manager.export_conjugations_csv("verb_conjugations.csv")

# Create backup
dict_manager.save_dictionary("dictionary_backup.json")

# Get statistics
stats = dict_manager.get_stats()
print(f"Total words: {stats['total_words']}")
print(f"Verbs with conjugations: {stats['verbs_with_conjugations']}")
```

## 📱 Future Enhancements

- [ ] Mobile-friendly web interface
- [ ] Audio pronunciation integration
- [ ] Spaced repetition flashcard system
- [ ] Progress tracking and learning analytics
- [ ] Integration with Italian learning apps
- [ ] Advanced search with filters
- [ ] Phrase and sentence examples
- [ ] Regional variation support

## 📄 License

This is a personal learning project. Feel free to use as reference for your own language learning projects.

---

**Happy Italian Learning! 🍝📚**

*"Una lingua diversa è una diversa visione della vita."*  
*("A different language is a different vision of life.")*