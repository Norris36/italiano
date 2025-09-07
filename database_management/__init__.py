"""
Database Management Package for Italian Dictionary
~~~
- PostgreSQL integration with pandas
- Data migration utilities
- Connection management
- Exercise generation from database
~~~
"""

from .database_manager import DatabaseManager, create_connection_from_env

__version__ = "1.0.0"
__author__ = "Italian Dictionary Project"

# Make main classes available at package level
__all__ = [
    'DatabaseManager',
    'create_connection_from_env'
]