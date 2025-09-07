# database_connection.py
import os
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """
    Get connection to Italian Dictionary PostgreSQL database
    """
    # Database connection parameters
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'italian_dictionary',
        'user': 'italian_user', 
        'password': 'your_password_here'  # Use from .env in production
    }
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def test_connection():
    """Test database connection"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM words;")
        word_count = cur.fetchone()[0]
        print(f"✅ Connected! Database has {word_count} words.")
        cur.close()
        conn.close()
        return True
    return False