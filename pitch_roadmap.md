# Italian Dictionary Project - Detailed Roadmap 🇮🇹

## Project Overview
Create a comprehensive Italian learning system focused on the top 1000 most frequent words using brute force memorization with analog PDF exercises. The system will be database-driven with automated CSV exports and multiple exercise formats.

---

## 🎯 **PHASE 1: Foundation Infrastructure** 
*Timeline: 2-3 weeks*

### **1.1 PostgreSQL Database Setup**
- [ ] Set up local PostgreSQL database
- [ ] Create database schema for words, conjugations, exercises, and progress tracking
- [ ] Design tables: `words`, `verbs`, `conjugations`, `exercises`, `user_progress` 
- [ ] Implement database connection utilities
- [ ] Create migration scripts
- [ ] Add data validation and constraints

### **1.2 CSV Automation System**
- [ ] Create automated CSV export scripts
- [ ] Set up GitHub Actions to update CSVs on schedule
- [ ] Generate static CSV files:
  - `verbs.csv` - All verb conjugations
  - `vocabulary.csv` - Top 1000 words with translations  
  - `exercises.csv` - Generated exercise sets
- [ ] Test raw.github access URLs
- [ ] Implement versioning for CSV files

### **1.3 Enhanced Dictionary Manager**
- [ ] Expand dictionary_manager.py for PostgreSQL integration
- [ ] Add frequency ranking system
- [ ] Implement word categorization (verbs, nouns, adjectives, etc.)
- [ ] Create word difficulty scoring algorithm
- [ ] Add spaced repetition metadata fields

---

## 🏗️ **PHASE 2: Content Expansion**
*Timeline: 3-4 weeks*

### **2.1 Verb Conjugation Completion**
- [ ] Complete missing tenses for current 7 verbs:
  - [ ] Imperfetto (5 verbs missing)
  - [ ] Passato Prossimo (4 verbs missing)
  - [ ] Futuro Semplice (7 verbs - HIGH PRIORITY)
  - [ ] Condizionale Presente (7 verbs)
  - [ ] Imperativo (7 verbs)
  - [ ] Congiuntivo Presente (7 verbs)

### **2.2 Top 100 Words Research**
- [ ] Research Italian word frequency data sources
- [ ] Compile definitive list of top 100 most frequent words
- [ ] Categorize by word type (verbs, nouns, adjectives, etc.)
- [ ] Add translations and usage examples
- [ ] Implement emoji support for visual context
- [ ] Add gender information for nouns

### **2.3 Extended Verb Collection**
- [ ] Add 50 most common verbs (positions 8-57)
- [ ] Focus on regular -are, -ere, -ire patterns
- [ ] Include essential irregular verbs
- [ ] Add auxiliary verb information
- [ ] Implement verb regularity classification

---

## 📝 **PHASE 3: Exercise Generation Engine**
*Timeline: 4-5 weeks*

### **3.1 Multiple Exercise Types**
- [ ] **Translation Exercises**:
  - [ ] English → Italian fill-in-the-blank
  - [ ] Italian → English multiple choice
  - [ ] Sentence completion with word bank
  - [ ] Context-based translation

- [ ] **Conjugation Exercises**:
  - [ ] Compact table format (6 persons per verb)
  - [ ] Mixed tense conjugation sheets
  - [ ] Irregular verb focus exercises
  - [ ] Progressive difficulty levels

- [ ] **Vocabulary Drills**:
  - [ ] Random word matching
  - [ ] Gender identification for nouns
  - [ ] Synonym/antonym exercises
  - [ ] Frequency-based word selection

### **3.2 Advanced PDF Generator**
- [ ] Enhance current PDF system for multiple formats
- [ ] Implement exercise type templates
- [ ] Add emoji integration for visual cues
- [ ] Create answer key formatting (tiny grey font)
- [ ] Maximize A4 page density
- [ ] Add difficulty progression indicators

### **3.3 Spaced Repetition Logic**
- [ ] Design algorithm for word difficulty tracking
- [ ] Implement "good words" vs "bad words" classification
- [ ] Create weighted random selection system
- [ ] Add progress tracking integration
- [ ] Design review scheduling system

---

## 🎲 **PHASE 4: Randomized Exercise System**
*Timeline: 2-3 weeks*

### **4.1 Stateless Exercise Generation**
- [ ] Create random exercise generator API
- [ ] Implement seed-based randomization for reproducibility
- [ ] Design exercise mixing algorithms
- [ ] Add difficulty balancing
- [ ] Create URL-based exercise parameters

### **4.2 Exercise Variety Engine**
- [ ] Mix multiple exercise types per page
- [ ] Implement smart question selection
- [ ] Add progressive difficulty scaling
- [ ] Create themed exercise sets (verbs only, nouns only, etc.)
- [ ] Implement answer distribution balancing

### **4.3 PDF Batch Generation**
- [ ] Create bulk PDF generation system
- [ ] Implement exercise series numbering
- [ ] Add metadata tracking for each generated set
- [ ] Create quality control checks
- [ ] Design exercise preview system

---

## 🗄️ **PHASE 5: Database Integration** 
*Timeline: 3-4 weeks*

### **5.1 PostgreSQL Schema Implementation**
```sql
-- Example table structures to implement:
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    english TEXT NOT NULL,
    italian TEXT[] NOT NULL,
    word_type VARCHAR(20),
    frequency_rank INTEGER,
    difficulty_score FLOAT,
    gender VARCHAR(10),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conjugations (
    id SERIAL PRIMARY KEY,
    verb_id INTEGER REFERENCES words(id),
    tense VARCHAR(30),
    person VARCHAR(10),
    conjugated_form TEXT,
    auxiliary VARCHAR(10)
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    exercise_type VARCHAR(50),
    content JSONB,
    difficulty_level INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **5.2 Data Migration**
- [ ] Migrate current dictionary.json to PostgreSQL
- [ ] Implement data validation and cleanup
- [ ] Create backup and restore procedures
- [ ] Add data integrity checks
- [ ] Implement change tracking

### **5.3 API Development**
- [ ] Create REST API for word management
- [ ] Implement exercise generation endpoints
- [ ] Add statistical reporting endpoints
- [ ] Create data export functionality
- [ ] Add authentication for admin functions

---

## 📊 **PHASE 6: Analytics & Optimization**
*Timeline: 2-3 weeks*

### **6.1 Progress Tracking (Optional)**
- [ ] Design progress tracking schema
- [ ] Implement anonymous session tracking
- [ ] Create performance analytics
- [ ] Add word mastery scoring
- [ ] Generate learning insights

### **6.2 Content Optimization**
- [ ] Analyze exercise effectiveness
- [ ] Implement A/B testing for formats
- [ ] Optimize word selection algorithms
- [ ] Fine-tune difficulty progression
- [ ] Create feedback collection system

### **6.3 Automation & Maintenance**
- [ ] Set up automated testing
- [ ] Create database maintenance scripts
- [ ] Implement CSV update scheduling
- [ ] Add error monitoring and alerts
- [ ] Create deployment automation

---

## 🚀 **PHASE 7: Scale to 1000 Words**
*Timeline: 8-10 weeks*

### **7.1 Content Expansion**
- [ ] Research and add words 101-300
- [ ] Research and add words 301-600
- [ ] Research and add words 601-1000
- [ ] Add specialized categories:
  - [ ] Food and cooking terms
  - [ ] Family and relationships
  - [ ] Travel and transportation
  - [ ] Work and professions
  - [ ] Emotions and feelings

### **7.2 Advanced Grammar**
- [ ] Add preposition exercises
- [ ] Include article usage (il, la, gli, le)
- [ ] Add adjective agreement rules
- [ ] Implement sentence construction exercises
- [ ] Create more complex conjugation drills

### **7.3 Quality Assurance**
- [ ] Native speaker review of all content
- [ ] Accuracy verification for all conjugations
- [ ] Cultural context validation
- [ ] Regional variation documentation
- [ ] Error correction and updates

---

## 🔧 **Technical Requirements**

### **Development Tools**
- Python 3.11+ with pandas, psycopg2, reportlab
- PostgreSQL 15+ (local installation)
- GitHub Actions for automation  
- Jupyter notebooks for development/testing

### **File Structure**
```
italian/
├── database/
│   ├── migrations/
│   ├── schema.sql
│   └── seed_data.sql
├── exports/
│   ├── verbs.csv
│   ├── vocabulary.csv
│   └── exercises.csv  
├── generators/
│   ├── exercise_generator.py
│   ├── pdf_generator.py (enhanced)
│   └── templates/
├── api/
│   ├── endpoints.py
│   ├── models.py
│   └── utils.py
└── scripts/
    ├── csv_updater.py
    ├── data_migration.py
    └── maintenance.py
```

---

## 📈 **Success Metrics**

### **Phase 1-3 Goals**
- [ ] 100 words with complete metadata
- [ ] 7 verbs with all major tenses
- [ ] 5 different exercise types working
- [ ] Automated CSV generation

### **Phase 4-6 Goals** 
- [ ] Stateless PDF generation working
- [ ] PostgreSQL integration complete
- [ ] Spaced repetition algorithm implemented
- [ ] 500 words in database

### **Phase 7 Goals**
- [ ] 1000 words complete
- [ ] 100+ verbs with conjugations
- [ ] Multiple exercise formats perfected
- [ ] Automated content delivery system

---

## ⚠️ **Risk Mitigation**

### **Technical Risks**
- PostgreSQL setup complexity → Provide docker-compose setup
- CSV automation reliability → Add error handling and monitoring
- PDF generation performance → Implement caching and batch processing

### **Content Risks**  
- Translation accuracy → Multiple source verification
- Frequency data reliability → Use multiple corpora sources
- Conjugation errors → Automated validation rules

### **Scope Risks**
- Feature creep → Stick to stateless PDF focus initially
- Perfectionism → Implement iterative releases
- Time management → Prioritize core functionality first

---

## 🎯 **Immediate Next Steps (Week 1)**

1. **Set up PostgreSQL locally** and create initial schema
2. **Enhance current PDF generator** with table-based conjugation exercises  
3. **Complete Futuro Semplice** conjugations for all 7 verbs
4. **Create CSV export automation** script
5. **Research Italian word frequency** sources for top 100 list

---

*This roadmap is designed to be iterative - adjust priorities and timelines based on learning progress and changing requirements. Focus on delivering working solutions at each phase rather than perfecting individual features.*