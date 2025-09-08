"""
Interactive Conjugation Exercise Generator
~~~
- Generate HTML conjugation sheets with customizable dimensions
- Use configuration from HTML configurator
- Create both exercise and answer sheets
- Export to HTML and PDF formats
- Maximum density optimization for A4 printing
~~~
returns: HTML and PDF exercise sheets
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import webbrowser
import os
from pathlib import Path
import sys

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dictionary_manager import ItalianDictionary

class ConjugationExerciseGenerator:
    """
    Generate printable conjugation exercises from Italian dictionary
    ~~~
    - Load verb data from dictionary
    - Apply configuration settings
    - Generate HTML with precise dimensions
    - Create exercise and answer versions
    - Optimize for maximum page density
    ~~~
    returns: ConjugationExerciseGenerator instance
    """
    
    def __init__(self, dictionary_path: str = "dictionary.json"):
        """
        Initialize exercise generator
        ~~~
        - Load dictionary data
        - Set default configuration
        - Prepare verb data
        ~~~
        returns: None
        """
        self.dictionary = ItalianDictionary(dictionary_path)
        self.verbs = self._load_verbs()
        self.config = self._default_config()
    
    def _default_config(self) -> Dict:
        """
        Default configuration settings
        ~~~
        - Set default dimensions and font sizes
        - Configure exercise parameters
        ~~~
        returns: Dict with default configuration
        """
        return {
            'page_margin_cm': 1.27,
            'base_font_size': 10,
            'table_font_size': 9,
            'cell_padding': 3,
            'table_margin': 15,
            'verb_count': 12,
            'missing_count': 2,
            'tenses': ['presente'],
            'verb_selection': 'random',
            'show_infinitive': True,
            'show_english': True,
            'compact_mode': True
        }
    
    def _load_verbs(self) -> List[Dict]:
        """
        Load verb data from dictionary
        ~~~
        - Extract all verbs with conjugations
        - Format for exercise generation
        - Add frequency and regularity info
        ~~~
        returns: List of verb dictionaries
        """
        verbs = []
        
        # Access the words data directly from the dictionary data structure
        all_words = self.dictionary.data.get('words', {})
        
        for english_word, word_data in all_words.items():
            if word_data.get('type') == 'verb' and 'conjugations' in word_data:
                for italian_verb, tenses in word_data['conjugations'].items():
                    verb_entry = {
                        'english': english_word,
                        'italian': italian_verb,
                        'conjugations': tenses,
                        'frequency_rank': word_data.get('frequency_rank', 999),
                        'regularity': word_data.get('regularity', 'unknown'),
                        'category': word_data.get('category', 'general')
                    }
                    verbs.append(verb_entry)
        
        return sorted(verbs, key=lambda x: x['frequency_rank'])
    
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
        - Ensure required tenses exist
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
        
        # Ensure at least one tense is selected
        if not self.config['tenses']:
            self.config['tenses'] = ['presente']
    
    def select_verbs(self) -> List[Dict]:
        """
        Select verbs based on configuration
        ~~~
        - Apply selection criteria (random, frequent, etc.)
        - Filter by availability of required tenses
        - Return list of selected verbs
        ~~~
        returns: List of selected verbs
        """
        available_verbs = []
        
        # Filter verbs that have all required tenses
        for verb in self.verbs:
            has_all_tenses = all(tense in verb['conjugations'] for tense in self.config['tenses'])
            if has_all_tenses:
                available_verbs.append(verb)
        
        # Apply selection strategy
        selection = self.config['verb_selection']
        
        if selection == 'frequent':
            selected = available_verbs[:self.config['verb_count']]
        elif selection == 'irregular':
            irregular = [v for v in available_verbs if v['regularity'] == 'irregular']
            selected = irregular[:self.config['verb_count']]
        elif selection == 'regular':
            regular = [v for v in available_verbs if v['regularity'] == 'regular']
            selected = regular[:self.config['verb_count']]
        else:  # random
            selected = random.sample(available_verbs, min(self.config['verb_count'], len(available_verbs)))
        
        return selected
    
    def generate_missing_positions(self, verb: Dict) -> Dict[str, List[str]]:
        """
        Generate random missing conjugation positions
        ~~~
        - Select random persons to hide for each tense
        - Ensure variety across different verbs
        - Return mapping of tense -> missing persons
        ~~~
        returns: Dict mapping tenses to lists of missing persons
        """
        persons = ['io', 'tu', 'lui/lei', 'noi', 'voi', 'loro']
        missing_positions = {}
        
        for tense in self.config['tenses']:
            # Get random positions to hide
            positions_to_hide = random.sample(persons, min(self.config['missing_count'], len(persons)))
            missing_positions[tense] = positions_to_hide
        
        return missing_positions
    
    def generate_html_table(self, verb: Dict, missing_positions: Dict, show_answers: bool = False) -> str:
        """
        Generate HTML table for single verb
        ~~~
        - Create conjugation table with proper styling
        - Hide specified conjugations if not showing answers
        - Apply configuration styling
        ~~~
        returns: str with HTML table
        """
        persons = ['io', 'tu', 'lui/lei', 'noi', 'voi', 'loro']
        html_parts = []
        
        for tense in self.config['tenses']:
            if tense not in verb['conjugations']:
                continue
            
            conjugations = verb['conjugations'][tense]
            missing_for_tense = missing_positions.get(tense, [])
            
            # Table header
            tense_display = tense.replace('_', ' ').title()
            header_text = f"{verb['english']} → {verb['italian']}"
            if len(self.config['tenses']) > 1:
                header_text += f" ({tense_display})"
            
            html_parts.append(f'''
                <table class="conjugation-table">
                    <thead>
                        <tr>
                            <th class="verb-header" colspan="7">{header_text}</th>
                        </tr>
                        <tr>
                            <th>Infinitive</th>
                            {' '.join([f'<th>{person}</th>' for person in persons])}
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="infinitive-cell"><strong>{verb['italian']}</strong></td>
            ''')
            
            # Conjugation cells
            for person in persons:
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
                margin-bottom: 20px;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
            }}
            
            .page-title {{
                font-size: {self.config['base_font_size'] + 4}px;
                font-weight: bold;
                color: #2c3e50;
            }}
            
            .page-info {{
                font-size: {self.config['base_font_size'] - 1}px;
                color: #666;
                margin-top: 5px;
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
                margin-bottom: 15px;
                font-size: {self.config['base_font_size'] - 1}px;
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
        tense_list = ', '.join([t.replace('_', ' ').title() for t in self.config['tenses']])
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Italian Conjugation Exercise - {timestamp}</title>
            {self.generate_css()}
        </head>
        <body>
            <div class="page-container">
                <div class="page-header">
                    <div class="page-title">🇮🇹 Italian Conjugation Exercise</div>
                    <div class="page-info">{timestamp}</div>
                </div>
                
                <div class="exercise-info">
                    <strong>Instructions:</strong> Fill in the missing conjugations. 
                    Tenses: {tense_list} | 
                    Verbs: {len(selected_verbs)} | 
                    Missing per verb: {self.config['missing_count']}
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
        tense_list = ', '.join([t.replace('_', ' ').title() for t in self.config['tenses']])
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Italian Conjugation Answers - {timestamp}</title>
            {self.generate_css()}
        </head>
        <body>
            <div class="page-container answer-sheet">
                <div class="page-header">
                    <div class="page-title">🇮🇹 Italian Conjugation Answers</div>
                    <div class="page-info">{timestamp}</div>
                </div>
                
                <div class="exercise-info">
                    <strong>Answer Key:</strong> Previously missing conjugations are highlighted. 
                    Tenses: {tense_list} | 
                    Verbs: {len(selected_verbs)} | 
                    Missing per verb: {self.config['missing_count']}
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
        exercise_file = os.path.join(output_dir, f"conjugation_exercise_{timestamp}.html")
        answer_file = os.path.join(output_dir, f"conjugation_answers_{timestamp}.html")
        
        with open(exercise_file, 'w', encoding='utf-8') as f:
            f.write(exercise_html)
        
        with open(answer_file, 'w', encoding='utf-8') as f:
            f.write(answer_html)
        
        print(f"✅ Generated exercise sheet: {exercise_file}")
        print(f"✅ Generated answer sheet: {answer_file}")
        
        return exercise_file, answer_file
    
    def generate_exercises_from_config(self, config_file: str, output_dir: str = "output") -> Tuple[str, str]:
        """
        Generate exercises using saved configuration
        ~~~
        - Load configuration from file
        - Apply settings to current instance
        - Generate exercises with loaded settings
        ~~~
        returns: Tuple of (exercise_file, answer_file) paths
        """
        print(f"📄 Loading configuration from: {config_file}")
        self.load_config(config_file=config_file)
        
        print("⚙️  Applied configuration:")
        print(f"   • Page margins: {self.config['page_margin_cm']}cm")
        print(f"   • Base font: {self.config['base_font_size']}px")
        print(f"   • Table font: {self.config['table_font_size']}px")
        print(f"   • Verb count: {self.config['verb_count']}")
        print(f"   • Missing count: {self.config['missing_count']}")
        print(f"   • Tenses: {', '.join(self.config['tenses'])}")
        print(f"   • Selection: {self.config['verb_selection']}")
        
        return self.generate_exercises(output_dir)
    
    def export_to_pdf(self, html_file: str, pdf_file: str = None) -> str:
        """
        Export HTML exercise to PDF using weasyprint
        ~~~
        - Convert HTML to PDF with proper print settings
        - Maintain exact dimensions and formatting
        - Return path to generated PDF
        ~~~
        returns: str with PDF file path
        """
        try:
            import weasyprint
            
            if pdf_file is None:
                pdf_file = html_file.replace('.html', '.pdf')
            
            # Create CSS with print-specific optimizations
            print_css = weasyprint.CSS(string='''
                @page {
                    size: A4;
                    margin: 0;
                }
                body {
                    margin: 0;
                    padding: 0;
                }
                .page-container {
                    box-shadow: none !important;
                }
            ''')
            
            # Convert HTML to PDF
            weasyprint.HTML(filename=html_file).write_pdf(pdf_file, stylesheets=[print_css])
            print(f"📄 Generated PDF: {pdf_file}")
            return pdf_file
            
        except ImportError:
            print("⚠️  weasyprint not installed. Install with: pip install weasyprint")
            print("💡 Alternatively, use browser 'Print to PDF' function")
            return None
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return None
    
    def open_configurator(self) -> None:
        """
        Open the HTML configurator in browser
        ~~~
        - Launch configurator webpage
        - Allow real-time configuration
        ~~~
        returns: None
        """
        configurator_path = os.path.join(os.path.dirname(__file__), 'conjugation_configurator.html')
        webbrowser.open(f'file://{os.path.abspath(configurator_path)}')
        print(f"🌐 Opened configurator: {configurator_path}")


def main():
    """
    Main function for command line usage
    ~~~
    - Parse command line arguments
    - Generate exercises with different options
    - Demonstrate usage
    ~~~
    returns: None
    """
    import sys
    
    print("🇮🇹 Italian Conjugation Exercise Generator")
    print("=" * 50)
    
    # Create generator
    generator = ConjugationExerciseGenerator()
    
    print(f"📚 Loaded {len(generator.verbs)} verbs from dictionary")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        
        if action == 'config' and len(sys.argv) > 2:
            # Generate using saved configuration
            config_file = sys.argv[2]
            print(f"\n📄 Using configuration file: {config_file}")
            exercise_file, answer_file = generator.generate_exercises_from_config(config_file)
            
            # Optional PDF export
            if '--pdf' in sys.argv:
                print("\n📄 Exporting to PDF...")
                generator.export_to_pdf(exercise_file)
                generator.export_to_pdf(answer_file)
            
        elif action == 'configurator':
            # Open configurator
            print("\n🌐 Opening HTML configurator...")
            generator.open_configurator()
            return
            
        elif action == 'help':
            print_help()
            return
    
    else:
        # Interactive mode - show options
        print("\n🚀 Quick Start Options:")
        print("   1. Generate with default settings")
        print("   2. Open HTML configurator for custom settings")
        print("   3. Show example configurations")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '2':
            generator.open_configurator()
            return
        elif choice == '3':
            show_example_configurations(generator)
            return
    
    # Generate with default configuration
    print("\n🔄 Generating exercises with default configuration...")
    exercise_file, answer_file = generator.generate_exercises()
    
    print(f"\n🌐 Opening exercise in browser...")
    webbrowser.open(f'file://{os.path.abspath(exercise_file)}')
    
    print_usage_tips()

def show_example_configurations(generator):
    """Show and generate example configurations"""
    configurations = {
        'quick_presente': {
            'verb_count': 8,
            'tenses': ['presente'],
            'missing_count': 2,
            'verb_selection': 'frequent',
            'page_margin_cm': 1.0,
            'table_font_size': 9
        },
        'comprehensive': {
            'verb_count': 15,
            'tenses': ['presente', 'imperfetto'],
            'missing_count': 3,
            'verb_selection': 'random',
            'page_margin_cm': 1.27,
            'table_font_size': 8
        },
        'irregular_focus': {
            'verb_count': 10,
            'tenses': ['presente'],
            'missing_count': 2,
            'verb_selection': 'irregular',
            'page_margin_cm': 1.0,
            'table_font_size': 9
        },
        'maximum_density': {
            'verb_count': 20,
            'tenses': ['presente'],
            'missing_count': 2,
            'verb_selection': 'frequent',
            'page_margin_cm': 0.8,
            'base_font_size': 9,
            'table_font_size': 7,
            'cell_padding': 2,
            'table_margin': 10
        }
    }
    
    print("\n📝 Example configurations:")
    for name, config in configurations.items():
        tenses = ', '.join(config['tenses'])
        print(f"   {name}: {config['verb_count']} verbs, {tenses}, {config['verb_selection']} selection")
    
    choice = input(f"\nSelect configuration ({', '.join(configurations.keys())}): ").strip()
    
    if choice in configurations:
        print(f"\n⚙️  Applying {choice} configuration...")
        generator.load_config(config_dict=configurations[choice])
        exercise_file, answer_file = generator.generate_exercises()
        webbrowser.open(f'file://{os.path.abspath(exercise_file)}')
    else:
        print("❌ Invalid choice")

def print_help():
    """Print command line usage help"""
    print("""
🇮🇹 Italian Conjugation Exercise Generator - Command Line Usage

USAGE:
    python conjugation_generator.py [command] [options]

COMMANDS:
    (no command)     Interactive mode with options menu
    config <file>    Generate using saved configuration file
    configurator     Open HTML configurator in browser
    help             Show this help message

OPTIONS:
    --pdf           Export to PDF (requires weasyprint)

EXAMPLES:
    python conjugation_generator.py
        → Interactive mode
    
    python conjugation_generator.py configurator
        → Open HTML configurator
    
    python conjugation_generator.py config my_settings.json
        → Generate using saved configuration
    
    python conjugation_generator.py config my_settings.json --pdf
        → Generate and export to PDF

WORKFLOW:
    1. Run 'python conjugation_generator.py configurator'
    2. Adjust settings in the HTML interface
    3. Export configuration to JSON file
    4. Run 'python conjugation_generator.py config exported_config.json'
    """)

def print_usage_tips():
    """Print usage tips"""
    print(f"\n💡 Tips:")
    print(f"   • Open conjugation_configurator.html to customize dimensions")
    print(f"   • Use 'python conjugation_generator.py config <file>' with saved settings")
    print(f"   • Add --pdf flag to export PDF versions")
    print(f"   • Exercise files are saved in the 'output' directory")
    print(f"   • Use browser 'Print to PDF' if weasyprint unavailable")


if __name__ == "__main__":
    main()