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
        # Create a temporary PDF with the main content
        temp_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            temp_buffer,
            pagesize=self.page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build the main content
        story = self.create_quiz_content()
        
        # Add page break before answers
        story.append(PageBreak())
        
        # Build the document
        doc.build(story)
        
        # Now create the final PDF with upside-down answers
        temp_buffer.seek(0)
        existing_pdf = temp_buffer.getvalue()
        
        # Create the final PDF
        c = canvas.Canvas(self.output_filename, pagesize=self.page_size)
        
        # First, copy all pages from the temporary PDF
        from PyPDF2 import PdfReader, PdfWriter
        import io
        
        # Read the temporary PDF
        temp_pdf = PdfReader(io.BytesIO(existing_pdf))
        
        # Create a new PDF with the content and upside-down answers
        from reportlab.pdfgen import canvas
        
        # Alternative approach: Generate everything in one go with custom canvas
        self._generate_complete_pdf_with_canvas()
        
        print(f"PDF generated successfully: {self.output_filename}")
    
    def _generate_complete_pdf_with_canvas(self):
        """Generate the complete PDF using canvas for better control."""
        c = canvas.Canvas(self.output_filename, pagesize=self.page_size)
        
        # Page 1: Questions
        y_position = self.height - 72  # Start from top with margin
        
        # Title
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor('#2C3E50'))
        c.drawCentredString(self.width/2, y_position, self.title)
        y_position -= 40
        
        # Date and instructions
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(72, y_position, f"Date: {datetime.now().strftime('%B %d, %Y')}")
        y_position -= 20
        
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(72, y_position, "Instructions: Answer all questions. Check answers at the bottom when complete.")
        y_position -= 40
        
        # Questions
        for idx, row in self.df.iterrows():
            question_num = idx + 1
            
            # Check if we need a new page
            if y_position < 200:  # Leave space for answers
                c.showPage()
                y_position = self.height - 72
            
            # Question number
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.HexColor('#2C3E50'))
            c.drawString(72, y_position, f"Question {question_num}")
            y_position -= 20
            
            # Question text
            if pd.notna(row['question']) and str(row['question']).strip():
                c.setFont("Helvetica", 11)
                c.setFillColor(colors.black)
                # Wrap long text
                text = str(row['question'])
                words = text.split()
                line = ""
                x_indent = 90
                for word in words:
                    test_line = line + " " + word if line else word
                    if c.stringWidth(test_line, "Helvetica", 11) < (self.width - 144):
                        line = test_line
                    else:
                        c.drawString(x_indent, y_position, line)
                        y_position -= 15
                        line = word
                if line:
                    c.drawString(x_indent, y_position, line)
                    y_position -= 20
            
            # Task text
            if pd.notna(row['task']) and str(row['task']).strip():
                c.setFont("Helvetica-Oblique", 10)
                c.setFillColor(colors.HexColor('#555555'))
                task_text = f"Task: {str(row['task'])}"
                # Wrap task text similarly
                words = task_text.split()
                line = ""
                x_indent = 90
                for word in words:
                    test_line = line + " " + word if line else word
                    if c.stringWidth(test_line, "Helvetica-Oblique", 10) < (self.width - 144):
                        line = test_line
                    else:
                        c.drawString(x_indent, y_position, line)
                        y_position -= 15
                        line = word
                if line:
                    c.drawString(x_indent, y_position, line)
                    y_position -= 20
            
            # Answer line
            c.setStrokeColor(colors.grey)
            c.line(90, y_position, self.width - 72, y_position)
            y_position -= 35
        
        # New page for answers
        c.showPage()
        
        # Draw answers upside down at the bottom
        c.saveState()
        
        # Translate to bottom of page and rotate 180 degrees
        c.translate(self.width/2, 150)
        c.rotate(180)
        
        # Answer header
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.HexColor('#2C3E50'))
        c.drawCentredString(0, 0, "ANSWER KEY")
        
        # Answers
        y_offset = 25
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor('#666666'))
        
        for idx, row in self.df.iterrows():
            question_num = idx + 1
            answer = str(row['answer']) if pd.notna(row['answer']) else "No answer provided"
            answer_text = f"Question {question_num}: {answer}"
            
            # Center the answers
            c.drawCentredString(0, y_offset, answer_text)
            y_offset += 15
            
            # Check if we need to wrap to multiple columns or pages
            if y_offset > 120:
                y_offset = 25
                c.translate(200, 0)  # Move to next column
        
        c.restoreState()
        
        # Save the PDF
        c.save()
        print(f"PDF generated successfully: {self.output_filename}")

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