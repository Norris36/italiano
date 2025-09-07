# Database Management Package 🐘

Complete PostgreSQL database management system for the Italian Dictionary project, with pandas integration and automated setup scripts.

## 📁 **Package Structure**

```
database_management/
├── __init__.py                 # Package initialization
├── database_manager.py         # Main database operations
├── config.py                   # Configuration management
├── postgres_setup_guide.md     # Docker PostgreSQL setup
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
cd database_management/
pip install -r requirements.txt
```

### **2. Setup PostgreSQL Database**
Follow the comprehensive guide in [`postgres_setup_guide.md`](./postgres_setup_guide.md) to:
- Create separate database repository with Docker
- Set up automated start/stop scripts
- Configure PostgreSQL with Italian dictionary schema

### **3. Configure Connection**
```python
from database_management import DatabaseManager

# Method 1: Use environment variables
db = DatabaseManager()

# Method 2: Specify connection details
db = DatabaseManager(
    host="localhost",
    port=5432,
    database="italian_dictionary",
    user="italian_user",
    password="your_password"
)
```

## 📊 **Core Features**

### **Pandas Integration**
```python
# Read database tables as DataFrames
words_df = db.get_all_words()
verbs_df = db.get_words_by_type('verb')
frequent_df = db.get_words_by_frequency(100)

# Write DataFrames to database
new_words = pd.DataFrame([...])
db.write_df_to_table(new_words, 'words')

# Custom SQL queries
results = db.query_to_df("""
    SELECT w.english, c.tense, COUNT(*) as conjugations
    FROM words w JOIN conjugations c ON w.id = c.word_id
    GROUP BY w.english, c.tense
""")
```

### **Vocabulary Management**
```python
# Add new words
db.add_word("cat", ["gatto"], "noun", frequency_rank=150, gender="masculine")

# Search functionality
results = db.search_words("casa", language="italian")
italian_words = db.search_words("house", language="english")

# Get words by category/type
essential_words = db.read_table_to_df("words", "category = 'essential'")
```

### **Conjugation Operations**
```python
# Add verb conjugations
presente_essere = {
    "io": "sono", "tu": "sei", "lui/lei": "è",
    "noi": "siamo", "voi": "siete", "loro": "sono"
}
db.add_conjugations(word_id=1, italian_verb="essere", 
                   tense="presente", conjugation_dict=presente_essere)

# Get conjugation data
all_conjugations = db.get_conjugations()
presente_only = db.get_conjugations(tense="presente")
verb_summary = db.get_verb_summary()
```

### **Exercise Generation**
```python
# Translation exercises
translation_ex = db.generate_translation_exercise(
    word_count=20, 
    word_type="noun"
)

# Conjugation exercises
conjugation_ex = db.generate_conjugation_exercise(
    verb_count=5, 
    tense="presente"
)

# Export for PDF generation
translation_ex.to_csv("exercises/translation_20_words.csv", index=False)
```

### **Data Migration**
```python
# Migrate existing dictionary.json to PostgreSQL
success = db.migrate_from_json("../dictionary.json")

if success:
    print("✅ Migration completed successfully!")
    
# Get migration statistics
stats = db.get_database_stats()
print(f"Migrated {stats['total_words']} words and {stats['total_conjugations']} conjugations")
```

## ⚙️ **Configuration Management**

### **Environment Variables**
```bash
# Database Connection
DB_HOST=localhost
DB_PORT=5432
POSTGRES_DB=italian_dictionary
POSTGRES_USER=italian_user
POSTGRES_PASSWORD=your_secure_password

# Connection Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600
```

### **Using Configuration Module**
```python
from database_management.config import get_config, setup_env_file

# Create .env template
setup_env_file()  # Creates .env.template

# Use configuration
config = get_config(".env")
connection_params = config.get_connection_params()
```

## 📈 **Database Schema**

### **Core Tables**
- **`words`**: Main vocabulary (English, Italian translations, metadata)
- **`conjugations`**: Verb conjugations by tense and person
- **`exercises`**: Generated exercise sets
- **`user_progress`**: Learning progress tracking (optional)
- **`word_relationships`**: Synonyms, antonyms, related words

### **Optimized Features**
- **Full-text search** indexes for English and Italian
- **Connection pooling** for performance
- **Automatic reconnection** with health checks
- **Transaction support** with rollback on errors

## 🔧 **Advanced Operations**

### **Batch Operations**
```python
# Bulk insert from CSV
new_words_df = pd.read_csv("new_vocabulary.csv")
db.write_df_to_table(new_words_df, "words", if_exists="append")

# Bulk export
db.export_to_csv("words", "italian_vocabulary_export.csv")
db.export_to_csv("conjugations", "verb_conjugations_export.csv")
```

### **Statistical Analysis**
```python
# Get comprehensive statistics
stats = db.get_database_stats()

# Analyze word frequency distribution
frequency_analysis = db.query_to_df("""
    SELECT 
        CASE 
            WHEN frequency_rank <= 100 THEN 'Top 100'
            WHEN frequency_rank <= 500 THEN 'Top 500'
            ELSE 'Beyond 500'
        END as frequency_group,
        COUNT(*) as word_count
    FROM words 
    WHERE frequency_rank IS NOT NULL
    GROUP BY frequency_group
    ORDER BY MIN(frequency_rank)
""")

print(frequency_analysis)
```

### **Connection Management**
```python
# Manual connection handling
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM words")
    count = cursor.fetchone()[0]
    print(f"Total words: {count}")

# Test connection health
if db.test_connection():
    print("✅ Database connection healthy")
else:
    print("❌ Database connection failed")
```

## 🔗 **Integration with Main Project**

### **Import in Main Italian Project**
```python
# From main italian directory
import sys
sys.path.append('./database_management')

from database_management import DatabaseManager

# Or use relative import
from .database_management import DatabaseManager
```

### **Exercise Generation for PDF**
```python
# Generate exercises for PDF creation
from database_management import DatabaseManager
import pdf_creator as pc

# Create database manager
db = DatabaseManager()

# Generate translation exercise
exercise_df = db.generate_translation_exercise(word_count=15)

# Convert to PDF format expected by QuizPDFGenerator
exercise_df['question'] = exercise_df['english'] 
exercise_df['task'] = 'Translate to Italian'
exercise_df['answer'] = exercise_df['italian'].apply(lambda x: x[0])

# Generate PDF
generator = pc.QuizPDFGenerator(exercise_df, title="Italian Vocabulary Quiz")
generator.generate_pdf()
```

## 🆘 **Troubleshooting**

### **Common Issues**

**Connection Refused:**
```python
# Check if database is running
docker-compose ps  # In your database repository

# Test connection
from database_management import DatabaseManager
db = DatabaseManager()
db.test_connection()
```

**Missing Dependencies:**
```bash
pip install psycopg2-binary SQLAlchemy pandas python-dotenv
```

**Environment Variables:**
```python
# Check current environment
import os
print("DB_HOST:", os.getenv('DB_HOST'))
print("POSTGRES_DB:", os.getenv('POSTGRES_DB'))

# Create configuration template
from database_management.config import setup_env_file
setup_env_file()  # Creates .env.template
```

**Migration Issues:**
```python
# Check JSON file format
import json
with open('dictionary.json') as f:
    data = json.load(f)
    print("Words found:", len(data.get('words', {})))

# Migrate with error handling
try:
    success = db.migrate_from_json('dictionary.json')
    print(f"Migration successful: {success}")
except Exception as e:
    print(f"Migration error: {e}")
```

## 📚 **Further Reading**

- **[PostgreSQL Setup Guide](./postgres_setup_guide.md)**: Complete Docker setup
- **[Main Project README](../README.md)**: Italian dictionary overview  
- **[SQLAlchemy Documentation](https://docs.sqlalchemy.org/)**: Advanced database operations
- **[Pandas Documentation](https://pandas.pydata.org/)**: DataFrame operations

---

*This database management system provides the foundation for scalable Italian vocabulary learning with powerful data analysis capabilities!* 🇮🇹📊