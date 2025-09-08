"""
Presente CSV Exercise Generator
~~~
- Generate HTML conjugation sheets from presente.csv
- Use static header with six person types
- Create both exercise and answer sheets
- Export to HTML and PDF formats
- Maximum density optimization for A4 printing
~~~
returns: HTML exercise sheets from CSV data
"""

import csv
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import webbrowser
import os
from pathlib import Path

class PresenteExerciseGenerator:
    """
    Generate printable conjugation exercises from presente.csv
    ~~~
    - Load verb data from CSV file
    - Apply configuration settings
    - Generate HTML with precise dimensions
    - Create exercise and answer versions
    - Optimize for maximum page density
    ~~~
    returns: PresenteExerciseGenerator instance
    """
    
    def __init__(self, csv_path: str = "presente.csv"):
        """
        Initialize exercise generator with CSV data
        ~~~
        - Load CSV data
        - Set default configuration
        - Prepare verb data with static header
        ~~~
        returns: None
        """
        self.csv_path = csv_path
        self.verbs = self._load_csv_verbs()
        self.config = self._default_config()
        self.person_headers = ['io', 'tu', 'lui/lei', 'noi', 'voi', 'loro']
    
    def _default_config(self) -> Dict:
        """
        Default configuration settings for maximum density
        ~~~
        - Set compact dimensions and font sizes
        - Configure exercise parameters for maximum words per page
        ~~~
        returns: Dict with default configuration
        """
        return {
            'page_margin_cm': 1.0,
            'base_font_size': 9,
            'table_font_size': 8,
            'cell_padding': 2,
            'table_margin': 8,
            'verb_count': 18,
            'missing_count': 2,
            'verb_selection': 'frequent',
            'show_infinitive': True,
            'show_english': True,
            'compact_mode': True
        }
    
    def _load_csv_verbs(self) -> List[Dict]:
        """
        Load verb data from presente.csv
        ~~~
        - Read CSV with semicolon delimiter
        - Parse conjugation columns
        - Format for exercise generation
        ~~~
        returns: List of verb dictionaries
        """
        verbs = []
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                # Use semicolon as delimiter based on the CSV format
                reader = csv.DictReader(f, delimiter=';')
                
                for i, row in enumerate(reader):
                    # Skip empty rows
                    if not row.get('infintive') or not row.get('english'):
                        continue
                    
                    # Parse conjugations from CSV columns
                    conjugations = {
                        'io': row.get('1st S', '').strip(),
                        'tu': row.get('2nd S', '').strip(), 
                        'lui/lei': row.get('3rd S', '').strip(),
                        'noi': row.get('1stP', '').strip(),
                        'voi': row.get('2ndP', '').strip(),
                        'loro': row.get('1', '').strip()  # Last column for 3rd plural
                    }
                    
                    # Clean up any empty conjugations
                    conjugations = {k: v for k, v in conjugations.items() if v}
                    
                    if len(conjugations) >= 4:  # Need at least 4 conjugations
                        verb_entry = {
                            'english': row.get('english', '').strip(),
                            'italian': row.get('infintive', '').strip(),
                            'conjugations': {'presente': conjugations},
                            'frequency_rank': i + 1,  # Use row order as frequency
                            'regularity': row.get('regularity', '').strip(),
                            'category': 'presente'
                        }
                        verbs.append(verb_entry)
                        
        except FileNotFoundError:
            print(f"❌ Error: {self.csv_path} not found")
            return []
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return []
        
        print(f"📚 Loaded {len(verbs)} verbs from {self.csv_path}")
        return verbs
    
    def load_config(self, config_file: str = None, config_dict: Dict = None) -> None:
        """
        Load configuration from file or dictionary
        ~~~
        - Parse configuration parameters
        - Validate settings
        - Apply to current instance
        ~~~
        returns: None
        """
        if config_dict:
            self.config.update(config_dict)
        elif config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
                
                # Try JSON format first (from HTML configurator export)
                if content.strip().startswith('{'):
                    try:
                        json_config = json.loads(content)
                        self.config.update(json_config)
                    except json.JSONDecodeError:
                        pass
                
                # Try Python format (EXERCISE_CONFIG dictionary)
                elif 'EXERCISE_CONFIG' in content:
                    try:
                        exec(content)
                        self.config.update(locals()['EXERCISE_CONFIG'])
                    except Exception as e:
                        print(f"Error loading Python config: {e}")
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """
        Validate configuration parameters
        ~~~
        - Check ranges for numeric values
        - Ensure required parameters exist
        - Validate verb selection options
        ~~~
        returns: None
        """
        # Clamp numeric values to reasonable ranges
        self.config['page_margin_cm'] = max(0.5, min(3.0, self.config['page_margin_cm']))
        self.config['base_font_size'] = max(6, min(16, self.config['base_font_size']))
        self.config['table_font_size'] = max(5, min(14, self.config['table_font_size']))
        self.config['cell_padding'] = max(1, min(10, self.config['cell_padding']))
        self.config['verb_count'] = max(1, min(30, self.config['verb_count']))
        self.config['missing_count'] = max(1, min(6, self.config['missing_count']))
    
    def select_verbs(self) -> List[Dict]:
        """
        Select verbs based on configuration
        ~~~
        - Apply selection criteria (random, frequent, etc.)
        - Return list of selected verbs
        ~~~
        returns: List of selected verbs
        """
        available_verbs = self.verbs.copy()
        
        # Apply selection strategy
        selection = self.config['verb_selection']
        
        if selection == 'frequent':
            selected = available_verbs[:self.config['verb_count']]
        elif selection == 'irregular':
            irregular = [v for v in available_verbs if 'ireg' in v.get('regularity', '').lower()]
            selected = irregular[:self.config['verb_count']]
        elif selection == 'regular':
            regular = [v for v in available_verbs if 'r.' in v.get('regularity', '').lower()]
            selected = regular[:self.config['verb_count']]
        else:  # random
            selected = random.sample(available_verbs, min(self.config['verb_count'], len(available_verbs)))
        
        return selected
    
    def generate_missing_positions(self, verb: Dict) -> Dict[str, List[str]]:
        """
        Generate random missing conjugation positions
        ~~~
        - Select random persons to hide for presente tense
        - Ensure variety across different verbs
        - Return mapping of tense -> missing persons
        ~~~
        returns: Dict mapping tenses to lists of missing persons
        """
        conjugations = verb['conjugations']['presente']
        available_persons = list(conjugations.keys())
        
        # Get random positions to hide
        positions_to_hide = random.sample(
            available_persons, 
            min(self.config['missing_count'], len(available_persons))
        )
        
        return {'presente': positions_to_hide}
    
    def generate_html_table(self, verb: Dict, missing_positions: Dict, show_answers: bool = False) -> str:
        """
        Generate HTML table for single verb with static header
        ~~~
        - Create compact conjugation table
        - Use static header with six person types
        - Hide specified conjugations if not showing answers
        - Minimize vertical space for maximum density
        ~~~
        returns: str with HTML table
        """
        conjugations = verb['conjugations']['presente']
        missing_for_tense = missing_positions.get('presente', [])
        
        # Compact header with just essential info
        regularity_marker = "●" if 'ireg' in verb.get('regularity', '').lower() else "○"
        header_text = f"{verb['italian']} {regularity_marker} {verb['english']}"
        
        html_parts = [f'''
            <table class="conjugation-table">
                <thead>
                    <tr>
                        <th class="verb-header" colspan="7">{header_text}</th>
                    </tr>
                    <tr class="person-header">
                        <th>Infinitive</th>
                        <th>io</th>
                        <th>tu</th>
                        <th>lui/lei</th>
                        <th>noi</th>
                        <th>voi</th>
                        <th>loro</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="infinitive-cell">{verb['italian']}</td>
        ''']
        
        # Conjugation cells for each person type (static order)
        for person in self.person_headers:
            conjugation = conjugations.get(person, '???')
            is_missing = person in missing_for_tense and not show_answers
            cell_class = 'missing-conjugation' if is_missing else ''
            cell_content = '_____' if is_missing else conjugation
            
            html_parts.append(f'<td class="{cell_class}">{cell_content}</td>')
        
        html_parts.append('''
                    </tr>
                </tbody>
            </table>
        ''')
        
        return ''.join(html_parts)
    
    def generate_css(self) -> str:
        """
        Generate CSS based on configuration
        ~~~
        - Apply all dimension and font settings
        - Create print-optimized styles
        - Include responsive design rules
        ~~~
        returns: str with CSS styles
        """
        return f"""
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Arial', sans-serif;
                font-size: {self.config['base_font_size']}px;
                line-height: 1.2;
                color: #333;
                background: white;
            }}
            
            .page-container {{
                width: 210mm;
                min-height: 297mm;
                margin: 0 auto;
                padding: {self.config['page_margin_cm']}cm;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            
            .page-header {{
                text-align: center;
                margin-bottom: 8px;
                border-bottom: 1px solid #333;
                padding-bottom: 4px;
            }}
            
            .page-title {{
                font-size: {self.config['base_font_size'] + 1}px;
                font-weight: bold;
                color: #2c3e50;
            }}
            
            .page-info {{
                font-size: {self.config['base_font_size'] - 2}px;
                color: #666;
                margin-top: 2px;
            }}
            
            .conjugation-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: {self.config['table_margin']}px;
                font-size: {self.config['table_font_size']}px;
                border: 1px solid #333;
            }}
            
            .conjugation-table th,
            .conjugation-table td {{
                border: 1px solid #333;
                padding: {self.config['cell_padding']}px;
                text-align: center;
                vertical-align: middle;
            }}
            
            .conjugation-table th {{
                background: #f8f9fa;
                font-weight: bold;
            }}
            
            .verb-header {{
                background: #2c3e50 !important;
                color: white !important;
                font-size: {self.config['table_font_size'] + 1}px;
                font-weight: bold;
            }}
            
            .infinitive-cell {{
                background: #e9ecef;
                font-weight: bold;
            }}
            
            .missing-conjugation {{
                background: #fff3cd !important;
                border: 2px dashed #ffc107 !important;
                font-weight: bold;
                color: #856404;
            }}
            
            .answer-sheet .missing-conjugation {{
                background: #d4edda !important;
                border: 2px solid #28a745 !important;
                color: #155724;
                font-weight: bold;
            }}
            
            .exercise-info {{
                margin-bottom: 8px;
                font-size: {self.config['base_font_size'] - 2}px;
                color: #666;
                text-align: center;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
            
            @media print {{
                body {{ 
                    background: white; 
                    margin: 0;
                    padding: 0;
                }}
                
                .page-container {{
                    box-shadow: none;
                    margin: 0;
                    padding: {self.config['page_margin_cm']}cm;
                    width: 100%;
                    min-height: auto;
                }}
                
                .no-print {{ display: none !important; }}
            }}
            
            @media screen {{
                body {{ background: #f5f5f5; padding: 20px; }}
            }}
        </style>
        """
    
    def generate_exercise_sheet(self, selected_verbs: List[Dict], missing_data: Dict) -> str:
        """
        Generate complete exercise sheet HTML
        ~~~
        - Create header with instructions
        - Generate all conjugation tables
        - Apply styling and formatting
        ~~~
        returns: str with complete HTML
        """
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Italian Presente Exercise - {timestamp}</title>
            {self.generate_css()}
        </head>
        <body>
            <div class="page-container">
                <div class="page-header">
                    <div class="page-title">🇮🇹 Italian Presente Conjugation Exercise</div>
                    <div class="page-info">{timestamp}</div>
                </div>
                
                <div class="exercise-info">
                    <strong>Instructions:</strong> Fill in the missing presente conjugations. 
                    Verbs: {len(selected_verbs)} | 
                    Missing per verb: {self.config['missing_count']} | 
                    Person types: io, tu, lui/lei, noi, voi, loro
                </div>
                
                <div class="tables-container">
        """
        
        for verb in selected_verbs:
            missing_positions = missing_data[f"{verb['english']}_{verb['italian']}"]
            html_content += self.generate_html_table(verb, missing_positions, show_answers=False)
        
        html_content += """
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def generate_answer_sheet(self, selected_verbs: List[Dict], missing_data: Dict) -> str:
        """
        Generate answer sheet HTML
        ~~~
        - Same format as exercise sheet
        - Show all conjugations
        - Highlight previously missing ones
        ~~~
        returns: str with answer sheet HTML
        """
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Italian Presente Answers - {timestamp}</title>
            {self.generate_css()}
        </head>
        <body>
            <div class="page-container answer-sheet">
                <div class="page-header">
                    <div class="page-title">🇮🇹 Italian Presente Conjugation Answers</div>
                    <div class="page-info">{timestamp}</div>
                </div>
                
                <div class="exercise-info">
                    <strong>Answer Key:</strong> Previously missing conjugations are highlighted. 
                    Verbs: {len(selected_verbs)} | 
                    Missing per verb: {self.config['missing_count']} | 
                    Person types: io, tu, lui/lei, noi, voi, loro
                </div>
                
                <div class="tables-container">
        """
        
        for verb in selected_verbs:
            missing_positions = missing_data[f"{verb['english']}_{verb['italian']}"]
            html_content += self.generate_html_table(verb, missing_positions, show_answers=True)
        
        html_content += """
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def generate_exercises(self, output_dir: str = "output") -> Tuple[str, str]:
        """
        Generate both exercise and answer sheets
        ~~~
        - Select verbs based on configuration
        - Generate missing conjugation positions
        - Create HTML files for both versions
        - Return file paths
        ~~~
        returns: Tuple of (exercise_file, answer_file) paths
        """
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Select verbs and generate missing positions
        selected_verbs = self.select_verbs()
        missing_data = {}
        
        for verb in selected_verbs:
            key = f"{verb['english']}_{verb['italian']}"
            missing_data[key] = self.generate_missing_positions(verb)
        
        # Generate HTML content
        exercise_html = self.generate_exercise_sheet(selected_verbs, missing_data)
        answer_html = self.generate_answer_sheet(selected_verbs, missing_data)
        
        # Save files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exercise_file = os.path.join(output_dir, f"presente_exercise_{timestamp}.html")
        answer_file = os.path.join(output_dir, f"presente_answers_{timestamp}.html")
        
        with open(exercise_file, 'w', encoding='utf-8') as f:
            f.write(exercise_html)
        
        with open(answer_file, 'w', encoding='utf-8') as f:
            f.write(answer_html)
        
        print(f"✅ Generated exercise sheet: {exercise_file}")
        print(f"✅ Generated answer sheet: {answer_file}")
        
        return exercise_file, answer_file


def main():
    """
    Main function for command line usage
    ~~~
    - Generate exercises from presente.csv
    - Demonstrate usage options
    ~~~
    returns: None
    """
    import sys
    
    print("🇮🇹 Italian Presente Conjugation Exercise Generator (CSV)")
    print("=" * 60)
    
    # Create generator
    generator = PresenteExerciseGenerator()
    
    if not generator.verbs:
        print("❌ No verbs loaded. Please check that presente.csv exists.")
        return
    
    print(f"📚 Loaded {len(generator.verbs)} verbs from presente.csv")
    
    # Show sample verbs
    print("\n🔤 Sample verbs loaded:")
    for i, verb in enumerate(generator.verbs[:5]):
        regularity = verb.get('regularity', 'unknown')
        print(f"   {i+1}. {verb['english']} → {verb['italian']} ({regularity})")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'config' and len(sys.argv) > 2:
            config_file = sys.argv[2]
            print(f"\n📄 Loading configuration from: {config_file}")
            generator.load_config(config_file=config_file)
        elif sys.argv[1] == 'help':
            print_help()
            return
    
    # Generate exercises
    print(f"\n🔄 Generating presente exercises...")
    exercise_file, answer_file = generator.generate_exercises()
    
    print(f"\n🌐 Opening exercise in browser...")
    webbrowser.open(f'file://{os.path.abspath(exercise_file)}')
    
    print(f"\n💡 Files generated:")
    print(f"   Exercise: {exercise_file}")
    print(f"   Answers: {answer_file}")
    print(f"   Use browser 'Print to PDF' to create PDF versions")


def print_help():
    """Print command line usage help"""
    print("""
🇮🇹 Presente Exercise Generator - Command Line Usage

USAGE:
    python presente_exercise_generator.py [command] [options]

COMMANDS:
    (no command)     Generate with default settings
    config <file>    Generate using saved configuration file
    help             Show this help message

EXAMPLES:
    python presente_exercise_generator.py
        → Generate with default settings from presente.csv
    
    python presente_exercise_generator.py config my_settings.json
        → Generate using saved configuration

WORKFLOW:
    1. Ensure presente.csv exists in the current directory
    2. Run script to generate HTML exercise sheets
    3. Open in browser and use 'Print to PDF' to create PDF versions
    4. Adjust font sizes and margins using configuration files
    """)


if __name__ == "__main__":
    main()