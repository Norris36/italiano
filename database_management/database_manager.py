"""
PostgreSQL Database Manager for Italian Dictionary Project
~~~
- Pandas-integrated database operations
- Connection management and error handling
- Data migration from JSON to PostgreSQL
- CRUD operations with DataFrame support
- Exercise generation and progress tracking
~~~
returns: DatabaseManager class for Italian learning system
"""

import pandas as pd
import psycopg2
import psycopg2.extras
from sqlalchemy import create_engine, text
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import numpy as np
from contextlib import contextmanager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages PostgreSQL database operations with pandas integration
    ~~~
    - Connect to PostgreSQL database
    - Read/write DataFrames to database tables
    - Migrate data from JSON dictionary
    - Generate exercises and track progress
    - Handle verb conjugations and vocabulary
    ~~~
    returns: DatabaseManager instance
    """
    
    def __init__(self, host: str = "localhost", port: int = 5432, 
                 database: str = "italian_dictionary", user: str = "italian_user", 
                 password: str = None):
        """
        Initialize database manager
        ~~~
        - Set connection parameters
        - Create SQLAlchemy engine for pandas
        - Test database connection
        ~~~
        returns: None
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password or self._get_password()
        }
        
        # Create SQLAlchemy engine for pandas operations
        self.engine = self._create_engine()
        self.test_connection()
    
    def _get_password(self) -> str:
        """
        Get database password from environment or prompt
        ~~~
        - Check environment variables
        - Prompt user if not found
        ~~~
        returns: str with database password
        """
        password = os.getenv('POSTGRES_PASSWORD')
        if not password:
            import getpass
            password = getpass.getpass("Enter PostgreSQL password: ")
        return password
    
    def _create_engine(self):
        """
        Create SQLAlchemy engine for pandas operations
        ~~~
        - Build connection string
        - Configure engine parameters
        - Enable connection pooling
        ~~~
        returns: SQLAlchemy engine
        """
        connection_string = (
            f"postgresql://{self.connection_params['user']}:"
            f"{self.connection_params['password']}@"
            f"{self.connection_params['host']}:"
            f"{self.connection_params['port']}/"
            f"{self.connection_params['database']}"
        )
        
        return create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    def test_connection(self) -> bool:
        """
        Test database connection
        ~~~
        - Attempt connection to database
        - Run simple query
        - Log connection status
        ~~~
        returns: bool indicating connection success
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"✅ Connected to PostgreSQL: {version[:50]}...")
                return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        ~~~
        - Provide connection with automatic cleanup
        - Handle errors gracefully
        - Ensure connections are closed
        ~~~
        returns: psycopg2 connection
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    # PANDAS DATABASE OPERATIONS
    
    def read_table_to_df(self, table_name: str, condition: str = None) -> pd.DataFrame:
        """
        Read database table to pandas DataFrame
        ~~~
        - Execute SELECT query
        - Return results as DataFrame
        - Support WHERE conditions
        ~~~
        returns: pandas DataFrame with table data
        """
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        
        try:
            df = pd.read_sql_query(query, self.engine)
            logger.info(f"📊 Loaded {len(df)} rows from {table_name}")
            return df
        except Exception as e:
            logger.error(f"Error reading {table_name}: {e}")
            return pd.DataFrame()
    
    def write_df_to_table(self, df: pd.DataFrame, table_name: str, 
                         if_exists: str = 'append', index: bool = False) -> bool:
        """
        Write pandas DataFrame to database table
        ~~~
        - Insert DataFrame into specified table
        - Handle conflicts with if_exists parameter
        - Support bulk operations
        ~~~
        returns: bool indicating success
        """
        try:
            rows_affected = df.to_sql(
                table_name, 
                self.engine, 
                if_exists=if_exists, 
                index=index,
                method='multi'
            )
            logger.info(f"💾 Wrote {len(df)} rows to {table_name}")
            return True
        except Exception as e:
            logger.error(f"Error writing to {table_name}: {e}")
            return False
    
    def query_to_df(self, query: str, params: Dict = None) -> pd.DataFrame:
        """
        Execute custom SQL query and return DataFrame
        ~~~
        - Run parameterized SQL query
        - Return results as DataFrame
        - Support complex joins and aggregations
        ~~~
        returns: pandas DataFrame with query results
        """
        try:
            df = pd.read_sql_query(query, self.engine, params=params)
            logger.info(f"🔍 Query returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Query error: {e}")
            return pd.DataFrame()
    
    # VOCABULARY OPERATIONS
    
    def get_all_words(self) -> pd.DataFrame:
        """
        Get all vocabulary words as DataFrame
        ~~~
        - Fetch complete word list
        - Include metadata and rankings
        ~~~
        returns: DataFrame with all words
        """
        return self.read_table_to_df('words')
    
    def get_words_by_type(self, word_type: str) -> pd.DataFrame:
        """
        Get words filtered by type (verb, noun, etc.)
        ~~~
        - Filter words by grammatical type
        - Return matching entries
        ~~~
        returns: DataFrame with words of specified type
        """
        return self.read_table_to_df('words', f"word_type = '{word_type}'")
    
    def get_words_by_frequency(self, limit: int = 100) -> pd.DataFrame:
        """
        Get most frequent words
        ~~~
        - Order by frequency ranking
        - Limit results to top N words
        ~~~
        returns: DataFrame with most frequent words
        """
        query = f"""
        SELECT * FROM words 
        WHERE frequency_rank IS NOT NULL 
        ORDER BY frequency_rank 
        LIMIT {limit}
        """
        return self.query_to_df(query)
    
    def add_word(self, english: str, italian: List[str], word_type: str,
                frequency_rank: int = None, **kwargs) -> bool:
        """
        Add new word to database
        ~~~
        - Insert word with metadata
        - Handle array data for translations
        - Support additional attributes
        ~~~
        returns: bool indicating success
        """
        word_data = {
            'english': english,
            'italian': italian,
            'word_type': word_type,
            'frequency_rank': frequency_rank,
            **kwargs
        }
        
        df = pd.DataFrame([word_data])
        return self.write_df_to_table(df, 'words')
    
    def search_words(self, search_term: str, language: str = 'both') -> pd.DataFrame:
        """
        Search for words in English or Italian
        ~~~
        - Full text search across languages
        - Support partial matching
        - Return ranked results
        ~~~
        returns: DataFrame with matching words
        """
        if language == 'english':
            condition = f"english ILIKE '%{search_term}%'"
        elif language == 'italian':
            condition = f"array_to_string(italian, ',') ILIKE '%{search_term}%'"
        else:  # both
            condition = f"""
            english ILIKE '%{search_term}%' OR 
            array_to_string(italian, ',') ILIKE '%{search_term}%'
            """
        
        return self.read_table_to_df('words', condition)
    
    # CONJUGATION OPERATIONS
    
    def get_conjugations(self, word_id: int = None, tense: str = None) -> pd.DataFrame:
        """
        Get verb conjugations as DataFrame
        ~~~
        - Filter by word ID or tense
        - Include all conjugation data
        ~~~
        returns: DataFrame with conjugations
        """
        conditions = []
        if word_id:
            conditions.append(f"word_id = {word_id}")
        if tense:
            conditions.append(f"tense = '{tense}'")
        
        condition = " AND ".join(conditions) if conditions else None
        return self.read_table_to_df('conjugations', condition)
    
    def add_conjugations(self, word_id: int, italian_verb: str, tense: str, 
                        conjugation_dict: Dict[str, str]) -> bool:
        """
        Add verb conjugations for specific tense
        ~~~
        - Insert conjugation data for all persons
        - Validate required persons present
        - Link to word entry
        ~~~
        returns: bool indicating success
        """
        required_persons = {"io", "tu", "lui/lei", "noi", "voi", "loro"}
        if not required_persons.issubset(set(conjugation_dict.keys())):
            missing = required_persons - set(conjugation_dict.keys())
            logger.error(f"Missing required persons: {missing}")
            return False
        
        conjugation_data = []
        for person, form in conjugation_dict.items():
            conjugation_data.append({
                'word_id': word_id,
                'italian_verb': italian_verb,
                'tense': tense,
                'person': person,
                'conjugated_form': form
            })
        
        df = pd.DataFrame(conjugation_data)
        return self.write_df_to_table(df, 'conjugations')
    
    def get_verb_summary(self) -> pd.DataFrame:
        """
        Get summary of verb conjugation completeness
        ~~~
        - Join words and conjugations tables
        - Count conjugations per verb/tense
        - Show completion status
        ~~~
        returns: DataFrame with verb conjugation summary
        """
        query = """
        SELECT 
            w.english,
            w.italian[1] as italian_verb,
            c.tense,
            COUNT(c.person) as persons_count,
            CASE WHEN COUNT(c.person) = 6 THEN 'Complete' ELSE 'Incomplete' END as status
        FROM words w
        LEFT JOIN conjugations c ON w.id = c.word_id
        WHERE w.word_type = 'verb'
        GROUP BY w.id, w.english, w.italian[1], c.tense
        ORDER BY w.frequency_rank, c.tense
        """
        return self.query_to_df(query)
    
    # EXERCISE OPERATIONS
    
    def generate_translation_exercise(self, word_count: int = 10, 
                                    word_type: str = None) -> pd.DataFrame:
        """
        Generate translation exercise data
        ~~~
        - Select random words for exercise
        - Filter by type if specified
        - Return exercise DataFrame
        ~~~
        returns: DataFrame with exercise questions
        """
        conditions = []
        if word_type:
            conditions.append(f"word_type = '{word_type}'")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
        SELECT english, italian, word_type, frequency_rank
        FROM words 
        {where_clause}
        ORDER BY RANDOM()
        LIMIT {word_count}
        """
        
        exercise_df = self.query_to_df(query)
        if not exercise_df.empty:
            exercise_df['question'] = exercise_df['english']
            exercise_df['answer'] = exercise_df['italian'].apply(lambda x: x[0] if x else '')
            exercise_df['task'] = 'Translate to Italian'
        
        return exercise_df
    
    def generate_conjugation_exercise(self, verb_count: int = 5, 
                                    tense: str = 'presente') -> pd.DataFrame:
        """
        Generate verb conjugation exercise
        ~~~
        - Select random verbs with conjugations
        - Filter by tense
        - Format for exercise display
        ~~~
        returns: DataFrame with conjugation exercise
        """
        query = f"""
        SELECT 
            w.english,
            w.italian[1] as italian_verb,
            c.tense,
            c.person,
            c.conjugated_form
        FROM words w
        JOIN conjugations c ON w.id = c.word_id
        WHERE w.word_type = 'verb' AND c.tense = '{tense}'
        ORDER BY RANDOM()
        LIMIT {verb_count * 6}
        """
        
        conjugations = self.query_to_df(query)
        
        if conjugations.empty:
            return pd.DataFrame()
        
        # Pivot to create exercise format
        exercise = conjugations.pivot_table(
            index=['english', 'italian_verb', 'tense'],
            columns='person',
            values='conjugated_form',
            aggfunc='first'
        ).reset_index()
        
        return exercise
    
    # DATA MIGRATION
    
    def migrate_from_json(self, json_file_path: str) -> bool:
        """
        Migrate data from JSON dictionary to PostgreSQL
        ~~~
        - Load existing dictionary.json
        - Parse words and conjugations
        - Insert into database tables
        ~~~
        returns: bool indicating migration success
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            words_data = []
            conjugations_data = []
            
            for english_word, word_info in data['words'].items():
                # Prepare word data
                word_row = {
                    'english': english_word,
                    'italian': word_info['translations'],
                    'word_type': word_info['type'],
                    'frequency_rank': word_info.get('frequency_rank'),
                    'regularity': word_info.get('regularity'),
                    'category': word_info.get('category'),
                    'gender': word_info.get('gender'),
                    'notes': word_info.get('notes')
                }
                words_data.append(word_row)
                
                # Process conjugations if present
                if 'conjugations' in word_info:
                    for italian_verb, tenses in word_info['conjugations'].items():
                        for tense, persons in tenses.items():
                            for person, form in persons.items():
                                conjugations_data.append({
                                    'english_word': english_word,  # Will need to resolve to word_id
                                    'italian_verb': italian_verb,
                                    'tense': tense,
                                    'person': person,
                                    'conjugated_form': form
                                })
            
            # Insert words
            words_df = pd.DataFrame(words_data)
            if not self.write_df_to_table(words_df, 'words', if_exists='replace'):
                return False
            
            # Get word IDs for conjugations
            if conjugations_data:
                # Resolve English words to word IDs
                word_id_map = {}
                words_in_db = self.get_all_words()
                for _, row in words_in_db.iterrows():
                    word_id_map[row['english']] = row['id']
                
                # Update conjugation data with word_ids
                for conj in conjugations_data:
                    conj['word_id'] = word_id_map.get(conj['english_word'])
                    del conj['english_word']
                
                # Insert conjugations
                conj_df = pd.DataFrame(conjugations_data)
                conj_df = conj_df.dropna(subset=['word_id'])  # Remove entries without word_id
                if not self.write_df_to_table(conj_df, 'conjugations', if_exists='replace'):
                    return False
            
            logger.info(f"✅ Migration complete: {len(words_data)} words, {len(conjugations_data)} conjugations")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    # STATISTICS AND REPORTING
    
    def get_database_stats(self) -> Dict:
        """
        Get comprehensive database statistics
        ~~~
        - Count records in all tables
        - Calculate completion percentages
        - Generate summary report
        ~~~
        returns: Dict with database statistics
        """
        stats = {}
        
        # Word counts
        words_df = self.get_all_words()
        stats['total_words'] = len(words_df)
        stats['words_by_type'] = words_df['word_type'].value_counts().to_dict()
        stats['words_by_category'] = words_df['category'].value_counts().to_dict()
        
        # Conjugation stats
        conjugations_df = self.read_table_to_df('conjugations')
        stats['total_conjugations'] = len(conjugations_df)
        
        if not conjugations_df.empty:
            stats['conjugations_by_tense'] = conjugations_df['tense'].value_counts().to_dict()
            stats['verbs_with_conjugations'] = conjugations_df['word_id'].nunique()
        
        # Exercise stats
        exercises_df = self.read_table_to_df('exercises')
        stats['total_exercises'] = len(exercises_df)
        
        return stats
    
    def export_to_csv(self, table_name: str, filename: str = None) -> str:
        """
        Export database table to CSV file
        ~~~
        - Read entire table to DataFrame
        - Export to CSV with UTF-8 encoding
        - Return filename
        ~~~
        returns: str with CSV filename
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{table_name}_{timestamp}.csv"
        
        df = self.read_table_to_df(table_name)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"📁 Exported {len(df)} rows to {filename}")
        return filename

# UTILITY FUNCTIONS

def create_connection_from_env() -> DatabaseManager:
    """
    Create database manager using environment variables
    ~~~
    - Read connection details from environment
    - Create DatabaseManager instance
    ~~~
    returns: DatabaseManager instance
    """
    return DatabaseManager(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('POSTGRES_DB', 'italian_dictionary'),
        user=os.getenv('POSTGRES_USER', 'italian_user'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def main():
    """
    Example usage and testing
    ~~~
    - Create database manager
    - Run basic operations
    - Display statistics
    ~~~
    returns: None
    """
    print("🇮🇹 Italian Dictionary Database Manager")
    print("=" * 50)
    
    # Create database manager
    try:
        db = create_connection_from_env()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    # Display statistics
    stats = db.get_database_stats()
    print("\n📊 Database Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Example operations
    print("\n🔍 Sample Queries:")
    
    # Get frequent words
    frequent_words = db.get_words_by_frequency(10)
    print(f"   Top 10 words: {len(frequent_words)} found")
    
    # Get verbs
    verbs = db.get_words_by_type('verb')
    print(f"   Verbs: {len(verbs)} found")
    
    # Conjugation summary
    verb_summary = db.get_verb_summary()
    print(f"   Verb conjugations: {len(verb_summary)} entries")

if __name__ == "__main__":
    main()