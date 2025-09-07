# PostgreSQL Docker Setup Guide for Italian Dictionary 🇮🇹🐘

## Overview
This guide will help you set up a **separate repository** with PostgreSQL running in Docker, including scripts to easily start/stop the database and connect it to your Italian dictionary project.

---

## 📁 **Step 1: Create Separate Database Repository**

### Create New Repository Structure
```bash
# Navigate to your parent directory
cd "/Users/jensbay/Dropbox/#1 Files/Life/private_programming/"

# Create new database repository
mkdir italian-database
cd italian-database

# Initialize git repository
git init
git remote add origin https://github.com/Norris36/italian-database.git
```

### Repository Structure
```
italian-database/
├── docker-compose.yml          # Main Docker configuration
├── Dockerfile                  # Custom PostgreSQL setup
├── scripts/
│   ├── start_db.sh            # Start database
│   ├── stop_db.sh             # Stop database  
│   ├── restart_db.sh          # Restart database
│   ├── connect_db.sh          # Connect to database
│   └── backup_db.sh           # Backup database
├── sql/
│   ├── init/
│   │   ├── 01_create_database.sql
│   │   ├── 02_create_schema.sql
│   │   └── 03_seed_data.sql
│   └── migrations/
├── data/                       # PostgreSQL data (gitignored)
├── backups/                    # Database backups
├── logs/                       # Database logs
├── .env.example               # Environment template
├── .gitignore
└── README.md
```

---

## 🐳 **Step 2: Docker Configuration Files**

### Create `docker-compose.yml`
```yaml
version: '3.8'

services:
  italian_postgres:
    build: .
    container_name: italian_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-italian_dictionary}
      POSTGRES_USER: ${POSTGRES_USER:-italian_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secure_password_123}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - ./data:/var/lib/postgresql/data
      - ./sql/init:/docker-entrypoint-initdb.d
      - ./backups:/backups
      - ./logs:/var/log/postgresql
    networks:
      - italian_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-italian_user} -d ${POSTGRES_DB:-italian_dictionary}"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

networks:
  italian_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
```

### Create `Dockerfile`
```dockerfile
FROM postgres:15-alpine

# Install additional tools
RUN apk add --no-cache \
    postgresql-contrib \
    postgresql-client \
    curl \
    bash

# Set timezone
RUN apk add --no-cache tzdata
ENV TZ=Europe/Rome

# Create backup directory
RUN mkdir -p /backups && chown postgres:postgres /backups

# Copy custom configuration
COPY --chown=postgres:postgres sql/init/ /docker-entrypoint-initdb.d/

# Expose port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1
```

### Create `.env.example`
```bash
# PostgreSQL Configuration
POSTGRES_DB=italian_dictionary
POSTGRES_USER=italian_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_PORT=5432

# Connection Settings
DB_HOST=localhost
DB_PORT=5432

# Backup Settings
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM

# Development Settings
PGADMIN_EMAIL=your_email@example.com
PGADMIN_PASSWORD=admin_password
PGADMIN_PORT=8080
```

---

## 🛠️ **Step 3: Database Management Scripts**

### Create `scripts/start_db.sh`
```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🇮🇹 Starting Italian Dictionary Database...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Navigate to database directory
cd "$(dirname "$0")/.."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env file with your settings before continuing.${NC}"
    echo -e "${YELLOW}Press Enter when ready...${NC}"
    read
fi

# Load environment variables
source .env

# Create necessary directories
mkdir -p data backups logs

# Start the database
echo -e "${YELLOW}🚀 Starting PostgreSQL container...${NC}"
docker-compose up -d

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if docker-compose exec -T italian_postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database is ready!${NC}"
        break
    fi
    counter=$((counter + 1))
    sleep 1
done

if [ $counter -eq $timeout ]; then
    echo -e "${RED}❌ Database failed to start within $timeout seconds${NC}"
    exit 1
fi

# Show connection info
echo -e "${GREEN}🎉 Italian Dictionary Database is running!${NC}"
echo -e "${GREEN}📊 Connection Details:${NC}"
echo -e "   Host: localhost"
echo -e "   Port: $POSTGRES_PORT"
echo -e "   Database: $POSTGRES_DB"
echo -e "   Username: $POSTGRES_USER"
echo ""
echo -e "${GREEN}🔗 Connection URL:${NC}"
echo -e "   postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:$POSTGRES_PORT/$POSTGRES_DB"
echo ""
echo -e "${YELLOW}💡 Quick Commands:${NC}"
echo -e "   Connect: ./scripts/connect_db.sh"
echo -e "   Stop:    ./scripts/stop_db.sh"
echo -e "   Restart: ./scripts/restart_db.sh"
```

### Create `scripts/stop_db.sh`
```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🇮🇹 Stopping Italian Dictionary Database...${NC}"

# Navigate to database directory
cd "$(dirname "$0")/.."

# Check if container is running
if ! docker-compose ps italian_postgres | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Database is not currently running.${NC}"
    exit 0
fi

# Stop the database
echo -e "${YELLOW}🛑 Stopping PostgreSQL container...${NC}"
docker-compose stop italian_postgres

echo -e "${GREEN}✅ Database stopped successfully!${NC}"
echo ""
echo -e "${YELLOW}💡 To start again: ./scripts/start_db.sh${NC}"
```

### Create `scripts/restart_db.sh`
```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🇮🇹 Restarting Italian Dictionary Database...${NC}"

# Navigate to database directory
cd "$(dirname "$0")/.."

echo -e "${YELLOW}🛑 Stopping database...${NC}"
docker-compose stop italian_postgres

echo -e "${YELLOW}🚀 Starting database...${NC}"
docker-compose start italian_postgres

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
source .env
timeout=30
counter=0

while [ $counter -lt $timeout ]; do
    if docker-compose exec -T italian_postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database restarted successfully!${NC}"
        break
    fi
    counter=$((counter + 1))
    sleep 1
done

if [ $counter -eq $timeout ]; then
    echo -e "${RED}❌ Database failed to restart within $timeout seconds${NC}"
    exit 1
fi
```

### Create `scripts/connect_db.sh`
```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🇮🇹 Connecting to Italian Dictionary Database...${NC}"

# Navigate to database directory
cd "$(dirname "$0")/.."

# Load environment variables
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi
source .env

# Check if database is running
if ! docker-compose ps italian_postgres | grep -q "Up"; then
    echo -e "${RED}❌ Database is not running. Start it first with: ./scripts/start_db.sh${NC}"
    exit 1
fi

# Connect to database
echo -e "${GREEN}🔌 Connecting to PostgreSQL...${NC}"
echo -e "${YELLOW}💡 Type '\\q' to exit${NC}"
echo ""

docker-compose exec italian_postgres psql -U $POSTGRES_USER -d $POSTGRES_DB
```

### Create `scripts/backup_db.sh`
```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🇮🇹 Backing up Italian Dictionary Database...${NC}"

# Navigate to database directory
cd "$(dirname "$0")/.."

# Load environment variables
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    exit 1
fi
source .env

# Check if database is running
if ! docker-compose ps italian_postgres | grep -q "Up"; then
    echo -e "${RED}❌ Database is not running. Start it first with: ./scripts/start_db.sh${NC}"
    exit 1
fi

# Create backup directory
mkdir -p backups

# Generate backup filename
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/italian_dictionary_${BACKUP_DATE}.sql"

echo -e "${YELLOW}💾 Creating backup: $BACKUP_FILE${NC}"

# Create backup
docker-compose exec -T italian_postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup created successfully!${NC}"
    echo -e "${GREEN}📁 File: $BACKUP_FILE${NC}"
    echo -e "${GREEN}📊 Size: $(du -h $BACKUP_FILE | cut -f1)${NC}"
else
    echo -e "${RED}❌ Backup failed!${NC}"
    exit 1
fi

# Clean up old backups (keep last 30 days)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
echo -e "${YELLOW}🧹 Cleaning up backups older than $RETENTION_DAYS days...${NC}"
find backups/ -name "italian_dictionary_*.sql" -mtime +$RETENTION_DAYS -delete

echo -e "${GREEN}🎉 Backup process completed!${NC}"
```

---

## 📊 **Step 4: Database Schema Files**

### Create `sql/init/01_create_database.sql`
```sql
-- Create Italian Dictionary Database Schema
-- This file is executed when the container starts for the first time

\echo 'Creating Italian Dictionary database schema...'

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For better text search

\echo 'Extensions created successfully'
```

### Create `sql/init/02_create_schema.sql`
```sql
-- Italian Dictionary Schema
-- Core tables for the Italian learning system

\echo 'Creating tables...'

-- Words table (main vocabulary)
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    english TEXT NOT NULL,
    italian TEXT[] NOT NULL,
    word_type VARCHAR(20) NOT NULL CHECK (word_type IN ('verb', 'noun', 'adjective', 'adverb', 'preposition', 'conjunction', 'article', 'pronoun')),
    frequency_rank INTEGER,
    difficulty_score FLOAT DEFAULT 1.0,
    gender VARCHAR(10) CHECK (gender IN ('masculine', 'feminine', 'neutral')),
    regularity VARCHAR(15) CHECK (regularity IN ('regular', 'irregular', 'mixed')),
    category VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Verb conjugations table
CREATE TABLE conjugations (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    italian_verb TEXT NOT NULL,
    tense VARCHAR(30) NOT NULL,
    person VARCHAR(10) NOT NULL CHECK (person IN ('io', 'tu', 'lui/lei', 'noi', 'voi', 'loro')),
    conjugated_form TEXT NOT NULL,
    auxiliary VARCHAR(10) CHECK (auxiliary IN ('essere', 'avere')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Exercise types and generated exercises
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    exercise_type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    content JSONB NOT NULL,
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 5),
    word_count INTEGER,
    estimated_time_minutes INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User progress tracking (optional)
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    session_id UUID DEFAULT uuid_generate_v4(),
    word_id INTEGER REFERENCES words(id),
    correct_count INTEGER DEFAULT 0,
    incorrect_count INTEGER DEFAULT 0,
    last_seen TIMESTAMP DEFAULT NOW(),
    mastery_level FLOAT DEFAULT 0.0,
    spaced_repetition_due TIMESTAMP DEFAULT NOW()
);

-- Word relationships (synonyms, antonyms, etc.)
CREATE TABLE word_relationships (
    id SERIAL PRIMARY KEY,
    word1_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    word2_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
    relationship_type VARCHAR(20) CHECK (relationship_type IN ('synonym', 'antonym', 'related')),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_words_frequency ON words(frequency_rank);
CREATE INDEX idx_words_type ON words(word_type);
CREATE INDEX idx_words_category ON words(category);
CREATE INDEX idx_conjugations_word_tense ON conjugations(word_id, tense);
CREATE INDEX idx_conjugations_tense ON conjugations(tense);
CREATE INDEX idx_user_progress_session ON user_progress(session_id);
CREATE INDEX idx_user_progress_due ON user_progress(spaced_repetition_due);

-- Full text search indexes
CREATE INDEX idx_words_english_search ON words USING gin(to_tsvector('english', english));
CREATE INDEX idx_words_italian_search ON words USING gin(to_tsvector('italian', array_to_string(italian, ' ')));

\echo 'Tables and indexes created successfully'
```

### Create `sql/init/03_seed_data.sql`
```sql
-- Seed data for Italian Dictionary
-- Initial data from current dictionary.json

\echo 'Inserting seed data...'

-- Insert essential verbs
INSERT INTO words (english, italian, word_type, frequency_rank, regularity, category, notes) VALUES
('be', ARRAY['essere'], 'verb', 1, 'irregular', 'essential', 'Most fundamental verb'),
('have', ARRAY['avere'], 'verb', 2, 'irregular', 'essential', 'Essential auxiliary verb'),
('go', ARRAY['andare'], 'verb', 3, 'irregular', 'essential', 'Motion verb'),
('do', ARRAY['fare'], 'verb', 4, 'irregular', 'essential', 'Action verb'),
('say', ARRAY['dire', 'parlare'], 'verb', 5, 'irregular', 'essential', 'dire = to say/tell, parlare = to speak/talk'),
('see', ARRAY['vedere'], 'verb', 6, 'irregular', 'essential', 'Perception verb'),
('know', ARRAY['sapere', 'conoscere'], 'verb', 7, 'irregular', 'essential', 'sapere = know facts, conoscere = know people/places');

-- Insert basic nouns and phrases
INSERT INTO words (english, italian, word_type, frequency_rank, category, gender) VALUES
('hello', ARRAY['ciao', 'salve'], 'noun', 8, 'greetings', NULL),
('goodbye', ARRAY['arrivederci', 'ciao'], 'noun', 9, 'greetings', NULL),
('thank you', ARRAY['grazie', 'ti ringrazio'], 'noun', 10, 'politeness', NULL),
('please', ARRAY['per favore', 'prego'], 'adverb', 11, 'politeness', NULL),
('water', ARRAY['acqua'], 'noun', 12, 'basic_needs', 'feminine'),
('food', ARRAY['cibo', 'mangiare'], 'noun', 13, 'basic_needs', 'masculine'),
('house', ARRAY['casa'], 'noun', 14, 'places', 'feminine'),
('money', ARRAY['denaro', 'soldi'], 'noun', 15, 'basic_needs', 'masculine'),
('time', ARRAY['tempo', 'ora'], 'noun', 16, 'concepts', 'masculine'),
('day', ARRAY['giorno'], 'noun', 17, 'time', 'masculine'),
('night', ARRAY['notte'], 'noun', 18, 'time', 'feminine'),
('good', ARRAY['buono', 'bene'], 'adjective', 19, 'descriptions', NULL),
('bad', ARRAY['cattivo', 'male'], 'adjective', 20, 'descriptions', NULL);

-- Insert conjugations for 'essere' (to be)
INSERT INTO conjugations (word_id, italian_verb, tense, person, conjugated_form, auxiliary) VALUES
-- Presente
(1, 'essere', 'presente', 'io', 'sono', 'essere'),
(1, 'essere', 'presente', 'tu', 'sei', 'essere'),
(1, 'essere', 'presente', 'lui/lei', 'è', 'essere'),
(1, 'essere', 'presente', 'noi', 'siamo', 'essere'),
(1, 'essere', 'presente', 'voi', 'siete', 'essere'),
(1, 'essere', 'presente', 'loro', 'sono', 'essere'),
-- Passato Prossimo
(1, 'essere', 'passato_prossimo', 'io', 'sono stato/a', 'essere'),
(1, 'essere', 'passato_prossimo', 'tu', 'sei stato/a', 'essere'),
(1, 'essere', 'passato_prossimo', 'lui/lei', 'è stato/a', 'essere'),
(1, 'essere', 'passato_prossimo', 'noi', 'siamo stati/e', 'essere'),
(1, 'essere', 'passato_prossimo', 'voi', 'siete stati/e', 'essere'),
(1, 'essere', 'passato_prossimo', 'loro', 'sono stati/e', 'essere'),
-- Imperfetto
(1, 'essere', 'imperfetto', 'io', 'ero', 'essere'),
(1, 'essere', 'imperfetto', 'tu', 'eri', 'essere'),
(1, 'essere', 'imperfetto', 'lui/lei', 'era', 'essere'),
(1, 'essere', 'imperfetto', 'noi', 'eravamo', 'essere'),
(1, 'essere', 'imperfetto', 'voi', 'eravate', 'essere'),
(1, 'essere', 'imperfetto', 'loro', 'erano', 'essere');

-- Insert conjugations for 'avere' (to have)
INSERT INTO conjugations (word_id, italian_verb, tense, person, conjugated_form, auxiliary) VALUES
-- Presente
(2, 'avere', 'presente', 'io', 'ho', 'avere'),
(2, 'avere', 'presente', 'tu', 'hai', 'avere'),
(2, 'avere', 'presente', 'lui/lei', 'ha', 'avere'),
(2, 'avere', 'presente', 'noi', 'abbiamo', 'avere'),
(2, 'avere', 'presente', 'voi', 'avete', 'avere'),
(2, 'avere', 'presente', 'loro', 'hanno', 'avere'),
-- Add more conjugations as needed...

\echo 'Seed data inserted successfully'
```

---

## 🚀 **Step 5: Usage Instructions**

### Make Scripts Executable
```bash
chmod +x scripts/*.sh
```

### Quick Start Commands
```bash
# Start database
./scripts/start_db.sh

# Connect to database
./scripts/connect_db.sh

# Stop database  
./scripts/stop_db.sh

# Restart database
./scripts/restart_db.sh

# Backup database
./scripts/backup_db.sh
```

### Create `.gitignore`
```
# Database data
data/
logs/
*.log

# Environment files
.env

# Backups (optional - you might want to commit some)
backups/*.sql

# Docker
.docker/
docker-compose.override.yml

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
```

---

## 🔗 **Step 6: Connect to Italian Dictionary Project**

### Update Italian Dictionary Connection
In your main `italian` project, create a database connection file:

```python
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
```

---

## 💡 **Pro Tips**

1. **Keep database repository separate** - This allows for independent database management
2. **Use environment variables** - Never commit passwords to git  
3. **Regular backups** - The backup script can be scheduled with cron
4. **Monitor resources** - PostgreSQL in Docker can use significant RAM
5. **Network access** - The database is accessible at `localhost:5432` from your main project

---

## 🆘 **Troubleshooting**

### Common Issues:
- **Port 5432 in use**: Change `POSTGRES_PORT` in `.env`
- **Permission denied**: Run `chmod +x scripts/*.sh`
- **Docker not running**: Start Docker Desktop first
- **Connection refused**: Wait for database to fully start (30-60 seconds)

### Useful Commands:
```bash
# Check if container is running
docker-compose ps

# View database logs
docker-compose logs italian_postgres

# Reset everything (⚠️ DESTROYS ALL DATA)
docker-compose down -v
rm -rf data/
./scripts/start_db.sh
```

This setup gives you a production-ready PostgreSQL database that's completely separate from your Italian dictionary project, with easy management scripts! 🚀