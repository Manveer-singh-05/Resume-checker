"""
PDF Generation Module
Creates ATS-friendly PDF resumes
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
from typing import Dict, Optional, Tuple
import os


class PDFGenerator:
    """Generate professional PDF resumes"""
    
    def __init__(self, output_dir: str = "output_resumes"):
        """
        Initialize PDF Generator
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_resume_pdf(
        self,
        resume_data: Dict[str, str],
        name: str = "Resume",
        contact_info: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Generate a PDF resume from resume data
        
        Args:
            resume_data: Dictionary with resume sections (summary, skills, experience, etc.)
            name: Name to use for the PDF file
            contact_info: Optional contact information (email, phone, location)
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name.replace(' ', '_')}_{timestamp}.pdf"
            file_path = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # Build the story
            story = []
            styles = self._get_custom_styles()
            
            # Add header with name and contact info
            if name:
                story.append(Paragraph(name, styles['title']))
                story.append(Spacer(1, 0.1*inch))
            
            if contact_info:
                contact_text = self._format_contact_info(contact_info)
                if contact_text:
                    story.append(Paragraph(contact_text, styles['contact']))
                    story.append(Spacer(1, 0.2*inch))
            
            # Add sections
            if resume_data.get('summary'):
                story.append(Paragraph("PROFESSIONAL SUMMARY", styles['section_heading']))
                story.append(Paragraph(resume_data['summary'], styles['body']))
                story.append(Spacer(1, 0.15*inch))
            
            if resume_data.get('skills'):
                story.append(Paragraph("SKILLS", styles['section_heading']))
                story.append(Paragraph(resume_data['skills'], styles['body']))
                story.append(Spacer(1, 0.15*inch))
            
            if resume_data.get('experience'):
                story.append(Paragraph("EXPERIENCE", styles['section_heading']))
                story.append(Paragraph(resume_data['experience'], styles['body']))
                story.append(Spacer(1, 0.15*inch))
            
            if resume_data.get('projects'):
                story.append(Paragraph("PROJECTS", styles['section_heading']))
                story.append(Paragraph(resume_data['projects'], styles['body']))
                story.append(Spacer(1, 0.15*inch))
            
            if resume_data.get('education'):
                story.append(Paragraph("EDUCATION", styles['section_heading']))
                story.append(Paragraph(resume_data['education'], styles['body']))
                story.append(Spacer(1, 0.15*inch))
            
            # Build PDF
            doc.build(story)
            
            return True, file_path, None
        except Exception as e:
            return False, "", f"Error generating PDF: {str(e)}"
    
    def _get_custom_styles(self):
        """Get custom paragraph styles for resume"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='title',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#1a1a1a',
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading style
        styles.add(ParagraphStyle(
            name='section_heading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor='#1a1a1a',
            spaceAfter=6,
            spaceBefore=6,
            fontName='Helvetica-Bold',
            borderPadding=4,
            leftIndent=0
        ))
        
        # Body style
        styles.add(ParagraphStyle(
            name='body',
            parent=styles['BodyText'],
            fontSize=9,
            leading=11,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        # Contact info style
        styles.add(ParagraphStyle(
            name='contact',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor='#333333',
            fontName='Helvetica'
        ))
        
        return styles
    
    def _format_contact_info(self, contact_info: Dict[str, str]) -> str:
        """Format contact information for header"""
        parts = []
        
        if contact_info.get('email'):
            parts.append(contact_info['email'])
        if contact_info.get('phone'):
            parts.append(contact_info['phone'])
        if contact_info.get('location'):
            parts.append(contact_info['location'])
        
        return " | ".join(parts)
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.output_dir):
                # Keep only recent files (last 24 hours)
                import time
                current_time = time.time()
                for filename in os.listdir(self.output_dir):
                    filepath = os.path.join(self.output_dir, filename)
                    if os.path.isfile(filepath):
                        if current_time - os.path.getmtime(filepath) > 86400:  # 24 hours
                            os.remove(filepath)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
