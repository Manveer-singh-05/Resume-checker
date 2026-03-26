"""
Resume Extraction Module
Extracts text from various resume formats (PDF, TXT, DOCX)
"""

import pdfplumber
import os
from typing import Tuple, Optional


class ResumeExtractor:
    """Extract text content from resume files"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            
            if not text.strip():
                return False, "", "No text found in PDF file"
            
            return True, text, None
        except Exception as e:
            return False, "", f"Error extracting PDF: {str(e)}"
    
    @staticmethod
    def extract_from_text(file_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from text file
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if not text.strip():
                return False, "", "Text file is empty"
            
            return True, text, None
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                return True, text, None
            except Exception as e:
                return False, "", f"Error reading text file: {str(e)}"
        except Exception as e:
            return False, "", f"Error reading file: {str(e)}"
    
    @staticmethod
    def extract_from_file(file_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Auto-detect file type and extract text
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        file_name = os.path.basename(file_path).lower()
        
        if file_name.endswith('.pdf'):
            return ResumeExtractor.extract_from_pdf(file_path)
        elif file_name.endswith('.txt'):
            return ResumeExtractor.extract_from_text(file_path)
        else:
            # Try as text first, then PDF
            success, text, error = ResumeExtractor.extract_from_text(file_path)
            if not success:
                return ResumeExtractor.extract_from_pdf(file_path)
            return success, text, error
    
    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            raw_text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        lines = raw_text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        text = '\n'.join(lines)
        
        # Remove common artifacts
        text = text.replace('\x00', '')
        text = text.replace('\x0c', '')
        
        return text
