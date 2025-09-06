import pandas as pd
import io
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class QuizPDFGenerator:
    def __init__(self, dataframe: pd.DataFrame, output_filename: str = "quiz.pdf", 
                 title: str = "Quiz", page_size=A4):
        """
        Initialize the Quiz PDF Generator.
        
        Args:
            dataframe: DataFrame with columns 'question', 'task', 'answer'
            output_filename: Name of the output PDF file
            title: Title of the quiz
            page_size: Page size (default A4, can use letter)
        """
        self.df = dataframe
        self.output_filename = output_filename
        self.title = title
        self.page_size = page_size
        self.width, self.height = page_size
        
        # Validate dataframe structure
        required_columns = ['question', 'task', 'answer']
        if not all(col in self.df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles for the PDF."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            bold=True
        ))
        
        # Question number style
        self.styles.add(ParagraphStyle(
            name='QuestionNumber',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            bold=True,
            spaceAfter=6
        ))
        
        # Question text style
        self.styles.add(ParagraphStyle(
            name='QuestionText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20,
            rightIndent=20
        ))
        
        # Task style
        self.styles.add(ParagraphStyle(
            name='TaskText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=20,
            fontName='Helvetica-Oblique'
        ))
        
        # Answer style (for upside down section)
        self.styles.add(ParagraphStyle(
            name='AnswerText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_LEFT
        ))
        
        # Answer header style
        self.styles.add(ParagraphStyle(
            name='AnswerHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            spaceAfter=15
        ))
    
    def create_quiz_content(self):
        """Create the main quiz content (questions and tasks)."""
        story = []
        
        # Add title
        title_para = Paragraph(self.title, self.styles['CustomTitle'])
        story.append(title_para)
        story.append(Spacer(1, 0.2*inch))
        
        # Add date and instructions
        date_text = f"Date: {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(date_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        instructions = "Instructions: Answer all questions in the space provided. Check your answers at the bottom of the page when complete."
        story.append(Paragraph(instructions, self.styles['Italic']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add questions
        for idx, row in self.df.iterrows():
            question_num = idx + 1
            
            # Keep question components together
            question_elements = []
            
            # Question number
            num_para = Paragraph(f"<b>Question {question_num}</b>", self.styles['QuestionNumber'])
            question_elements.append(num_para)
            
            # Question text
            if pd.notna(row['question']) and str(row['question']).strip():
                question_para = Paragraph(str(row['question']), self.styles['QuestionText'])
                question_elements.append(question_para)
            
            # Task text
            if pd.notna(row['task']) and str(row['task']).strip():
                task_para = Paragraph(f"<i>Task: {str(row['task'])}</i>", self.styles['TaskText'])
                question_elements.append(task_para)
            
            # Add answer space
            question_elements.append(Spacer(1, 0.3*inch))
            
            # Keep all question elements together
            story.append(KeepTogether(question_elements))
            
            # Add a line for writing space
            story.append(Paragraph("_" * 80, self.styles['Normal']))
            story.append(Spacer(1, 0.4*inch))
        
        return story
    
    def create_answer_section(self):
        """Create the answer section content."""
        answers = []
        
        # Create answer header
        answers.append(Paragraph("ANSWER KEY", self.styles['AnswerHeader']))
        answers.append(Spacer(1, 0.1*inch))
        
        # Compile all answers
        answer_text = []
        for idx, row in self.df.iterrows():
            question_num = idx + 1
            answer = str(row['answer']) if pd.notna(row['answer']) else "No answer provided"
            answer_text.append(f"Question {question_num}: {answer}")
        
        # Create answer paragraph
        full_answer_text = "<br/>".join(answer_text)
        answers.append(Paragraph(full_answer_text, self.styles['AnswerText']))
        
        return answers
    
    def generate_pdf(self):
        """Generate the complete PDF with upside-down answers."""
        # Use the canvas approach directly to avoid io conflicts
        self._generate_complete_pdf_with_canvas()
        print(f"PDF generated successfully: {self.output_filename}")
    
    def _generate_complete_pdf_with_canvas(self):
        """Generate dense, tabular PDF that fits everything on one page."""
        c = canvas.Canvas(self.output_filename, pagesize=self.page_size)
        
        # Standard 1.27cm margins all around (36 points)
        left_margin = 36
        right_margin = 36  
        top_margin = 36
        bottom_margin = 36
        
        # Calculate available space
        page_width = self.width - left_margin - right_margin
        page_height = self.height - top_margin - bottom_margin
        
        # Start position
        y_position = self.height - top_margin
        
        # Ultra-compact title
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.HexColor('#2C3E50'))
        c.drawString(left_margin, y_position, f"{self.title} - {datetime.now().strftime('%m/%d/%Y')}")
        y_position -= 15
        
        # Calculate space per question
        num_questions = len(self.df)
        answer_space_needed = 20  # Minimal space for answers at bottom
        available_question_space = y_position - bottom_margin - answer_space_needed
        space_per_question = available_question_space / num_questions if num_questions > 0 else 40
        
        # Ensure minimum space per question but much more compact
        space_per_question = max(space_per_question, 18)
        
        # Questions in tabular format
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.black)
        
        for idx, row in self.df.iterrows():
            if y_position <= bottom_margin + answer_space_needed:
                break  # Stop if we're running out of space
                
            question_num = idx + 1
            
            # Question number (ultra-compact)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(left_margin, y_position, f"{question_num}.")
            
            # Question and task text in one line if possible
            question_text = str(row['question']) if pd.notna(row['question']) else ""
            task_text = str(row['task']) if pd.notna(row['task']) else ""
            
            # Combine question and task
            combined_text = question_text
            if task_text and task_text != question_text:
                combined_text += f" [{task_text}]"
            
            # Truncate if too long to fit in available width
            c.setFont("Helvetica", 7)
            max_width = page_width - 25  # Leave minimal space for question number
            
            # Single line only - truncate if needed
            if c.stringWidth(combined_text, "Helvetica", 7) > max_width:
                # Truncate to fit
                while c.stringWidth(combined_text + "...", "Helvetica", 7) > max_width and len(combined_text) > 10:
                    combined_text = combined_text[:-1]
                combined_text += "..."
            
            # Draw the text in single line
            c.drawString(left_margin + 12, y_position, combined_text)
            
            # Answer line (from edge to edge)
            y_position -= 6
            c.setStrokeColor(colors.grey)
            c.setLineWidth(0.3)
            c.line(left_margin, y_position, self.width - right_margin, y_position)
            
            # Move to next question with minimal spacing
            y_position -= max(space_per_question - 12, 5)
        
        # Simple answers at very bottom - upside down
        c.saveState()
        c.translate(self.width/2, 20)  # Just above bottom margin
        c.rotate(180)
        c.setFont("Helvetica", 5)
        c.setFillColor(colors.HexColor('#666666'))
        
        # Create simple "1. answer 2. answer" format
        answer_parts = []
        for idx, row in self.df.iterrows():
            question_num = idx + 1
            answer = str(row['answer']) if pd.notna(row['answer']) else "N/A"
            # Truncate long answers
            if len(answer) > 15:
                answer = answer[:12] + "..."
            answer_parts.append(f"{question_num}. {answer}")
        
        # Join with spaces, truncate if too long for page width
        answer_line = " ".join(answer_parts)
        max_chars = int(page_width / 2.2)  # Approximate characters that fit
        if len(answer_line) > max_chars:
            answer_line = answer_line[:max_chars - 3] + "..."
        
        c.drawCentredString(0, 0, answer_line)
        c.restoreState()
        
        # Save the PDF
        c.save()

def create_sample_dataframe():
    """Create a sample dataframe for testing."""
    data = {
        'question': [
            'What is the capital of France?',
            'Calculate the area of a circle with radius 5cm.',
            'Translate "Good morning" to Spanish.',
            'What year did World War II end?',
            'Name three primary colors.',
            'What is photosynthesis?',
            'Solve for x: 2x + 5 = 15',
            'Who wrote "Romeo and Juliet"?',
            'What is the chemical symbol for water?',
            'Convert 32°F to Celsius.'
        ],
        'task': [
            'Write your answer below.',
            'Show your work and include the unit.',
            'Write the translation in Spanish.',
            'Provide the year only.',
            'List all three colors.',
            'Provide a brief definition.',
            'Show all steps of your solution.',
            'Write the author\'s full name.',
            'Write the chemical formula.',
            'Show the conversion formula and calculation.'
        ],
        'answer': [
            'Paris',
            '78.54 cm² (A = πr² = 3.14159 × 25)',
            'Buenos días',
            '1945',
            'Red, Blue, Yellow',
            'The process by which plants convert light energy into chemical energy',
            'x = 5 (2x = 10, x = 5)',
            'William Shakespeare',
            'H₂O',
            '0°C (32-32) × 5/9 = 0°C'
        ]
    }
    return pd.DataFrame(data)

def main():
    """Main function to demonstrate usage."""
    print("Quiz PDF Generator")
    print("=" * 50)
    
    # Check if user has a CSV file or wants to use sample data
    choice = input("\n1. Use sample data\n2. Load from CSV file\nChoose option (1 or 2): ")
    
    if choice == '2':
        filename = input("Enter CSV filename: ")
        try:
            df = pd.read_csv(filename)
            print(f"Loaded {len(df)} questions from {filename}")
        except FileNotFoundError:
            print("File not found. Using sample data instead.")
            df = create_sample_dataframe()
    else:
        df = create_sample_dataframe()
        print("Using sample data with 10 questions")
    
    # Get quiz details
    title = input("\nEnter quiz title (default: 'Practice Quiz'): ").strip()
    if not title:
        title = "Practice Quiz"
    
    output_file = input("Enter output filename (default: 'quiz.pdf'): ").strip()
    if not output_file:
        output_file = "quiz.pdf"
    if not output_file.endswith('.pdf'):
        output_file += '.pdf'
    
    # Generate PDF
    try:
        generator = QuizPDFGenerator(df, output_filename=output_file, title=title)
        generator.generate_pdf()
        print(f"\n✓ Success! Your quiz has been saved as '{output_file}'")
        print("The answers are printed upside-down at the bottom of the last page.")
    except Exception as e:
        print(f"\n✗ Error generating PDF: {e}")
        print("Make sure you have the required libraries installed:")
        print("pip install pandas reportlab PyPDF2")