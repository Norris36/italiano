"""
Database Configuration for Italian Dictionary
~~~
- Environment variable management
- Connection string building
- Default settings
- Configuration validation
~~~
returns: Configuration utilities and constants
"""

import os
from typing import Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """
    Manages database configuration settings
    ~~~
    - Load from environment variables
    - Provide default values
    - Validate configuration
    - Build connection parameters
    ~~~
    returns: DatabaseConfig instance
    """
    
    # Default configuration values
    DEFAULTS = {
        'host': 'localhost',
        'port': 5432,
        'database': 'italian_dictionary',
        'user': 'italian_user',
        'password': None,
        'pool_size': 5,
        'max_overflow': 10,
        'pool_recycle': 3600
    }
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration
        ~~~
        - Load environment variables
        - Apply defaults for missing values
        - Validate required settings
        ~~~
        returns: None
        """
        self.env_file = env_file
        self._load_env_file()
        self.config = self._build_config()
        self._validate_config()
    
    def _load_env_file(self):
        """
        Load environment file if specified
        ~~~
        - Check if .env file exists
        - Load variables into environment
        ~~~
        returns: None
        """
        if self.env_file and os.path.exists(self.env_file):
            try:
                from dotenv import load_dotenv
                load_dotenv(self.env_file)
                logger.info(f"Loaded environment from {self.env_file}")
            except ImportError:
                logger.warning("python-dotenv not available, skipping .env file")
    
    def _build_config(self) -> Dict:
        """
        Build configuration from environment and defaults
        ~~~
        - Read environment variables
        - Apply default values
        - Convert types as needed
        ~~~
        returns: Dict with configuration
        """
        config = {}
        
        # Database connection
        config['host'] = os.getenv('DB_HOST', self.DEFAULTS['host'])
        config['port'] = int(os.getenv('DB_PORT', self.DEFAULTS['port']))
        config['database'] = os.getenv('POSTGRES_DB', self.DEFAULTS['database'])
        config['user'] = os.getenv('POSTGRES_USER', self.DEFAULTS['user'])
        config['password'] = os.getenv('POSTGRES_PASSWORD', self.DEFAULTS['password'])
        
        # Connection pool settings
        config['pool_size'] = int(os.getenv('DB_POOL_SIZE', self.DEFAULTS['pool_size']))
        config['max_overflow'] = int(os.getenv('DB_MAX_OVERFLOW', self.DEFAULTS['max_overflow']))
        config['pool_recycle'] = int(os.getenv('DB_POOL_RECYCLE', self.DEFAULTS['pool_recycle']))
        
        return config
    
    def _validate_config(self):
        """
        Validate configuration values
        ~~~
        - Check required fields are present
        - Validate data types and ranges
        - Log configuration warnings
        ~~~
        returns: None
        """
        required_fields = ['host', 'port', 'database', 'user']
        missing_fields = [field for field in required_fields if not self.config.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {missing_fields}")
        
        if not self.config['password']:
            logger.warning("No database password configured - will prompt at runtime")
        
        if self.config['port'] < 1 or self.config['port'] > 65535:
            raise ValueError(f"Invalid port number: {self.config['port']}")
    
    def get_connection_params(self) -> Dict:
        """
        Get connection parameters for psycopg2
        ~~~
        - Return connection dictionary
        - Exclude None values
        ~~~
        returns: Dict with connection parameters
        """
        params = {
            'host': self.config['host'],
            'port': self.config['port'],
            'database': self.config['database'],
            'user': self.config['user']
        }
        
        if self.config['password']:
            params['password'] = self.config['password']
        
        return params
    
    def get_sqlalchemy_url(self, include_password: bool = True) -> str:
        """
        Build SQLAlchemy connection URL
        ~~~
        - Create PostgreSQL connection string
        - Optionally include password
        ~~~
        returns: str with connection URL
        """
        password = self.config['password'] if include_password else '***'
        
        if password:
            return (f"postgresql://{self.config['user']}:{password}@"
                   f"{self.config['host']}:{self.config['port']}/{self.config['database']}")
        else:
            return (f"postgresql://{self.config['user']}@"
                   f"{self.config['host']}:{self.config['port']}/{self.config['database']}")
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"DatabaseConfig({self.get_sqlalchemy_url(include_password=False)})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"DatabaseConfig(host='{self.config['host']}', "
               f"port={self.config['port']}, "
               f"database='{self.config['database']}', "
               f"user='{self.config['user']}')")

# Global configuration instance
_config = None

def get_config(env_file: Optional[str] = None) -> DatabaseConfig:
    """
    Get global configuration instance
    ~~~
    - Create singleton configuration
    - Load from environment file if provided
    ~~~
    returns: DatabaseConfig instance
    """
    global _config
    if _config is None or env_file:
        _config = DatabaseConfig(env_file)
    return _config

def get_connection_params() -> Dict:
    """
    Get connection parameters using global config
    ~~~
    - Use default configuration
    - Return parameters for database connection
    ~~~
    returns: Dict with connection parameters
    """
    return get_config().get_connection_params()

def get_sqlalchemy_url() -> str:
    """
    Get SQLAlchemy URL using global config
    ~~~
    - Use default configuration  
    - Return connection string
    ~~~
    returns: str with SQLAlchemy URL
    """
    return get_config().get_sqlalchemy_url()

# Environment setup helper
def setup_env_file():
    """
    Create .env file template for database configuration
    ~~~
    - Generate template with all options
    - Save to current directory
    ~~~
    returns: str with filename created
    """
    env_content = """# Italian Dictionary Database Configuration
# Copy this file to .env and fill in your values

# PostgreSQL Connection
DB_HOST=localhost
DB_PORT=5432
POSTGRES_DB=italian_dictionary
POSTGRES_USER=italian_user
POSTGRES_PASSWORD=your_secure_password_here

# Connection Pool Settings (optional)
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE=3600

# Development vs Production
ENVIRONMENT=development
DEBUG=True
"""
    
    env_file = Path('.env.template')
    env_file.write_text(env_content)
    logger.info(f"Created {env_file} - copy to .env and configure")
    return str(env_file)