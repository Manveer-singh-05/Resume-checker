"""
Utility Functions
Helper functions for file handling and validation
"""

import os
import mimetypes
from typing import Tuple, Optional


class FileValidator:
    """Validate and manage file uploads"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    @classmethod
    def validate_file(
        cls, 
        file_path: str, 
        max_size: int = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            file_path: Path to the file
            max_size: Maximum file size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in cls.ALLOWED_EXTENSIONS:
            return False, f"File type {ext} not supported. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}"
        
        # Check file size
        if max_size is None:
            max_size = cls.MAX_FILE_SIZE
        
        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return False, f"File too large. Maximum size: {max_size / 1024 / 1024:.1f} MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    @classmethod
    def get_mime_type(cls, file_path: str) -> str:
        """Get MIME type of file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"


class TextProcessor:
    """Process and clean text content"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for processing"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep structure
        text = text.replace('\x00', '')
        return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 2000) -> str:
        """Truncate text to maximum length"""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def count_lines(text: str) -> int:
        """Count lines in text"""
        return len(text.split('\n'))


class ResponseFormatter:
    """Format bot responses"""
    
    @staticmethod
    def format_score_response(score: float, max_score: int = 10) -> str:
        """Format matching score with visual indicator"""
        percentage = (score / max_score) * 100
        filled = int(percentage / 10)
        empty = 10 - filled
        
        bar = "█" * filled + "░" * empty
        status = "Excellent" if score >= 8 else "Good" if score >= 6 else "Fair" if score >= 4 else "Poor"
        
        return f"""
📊 MATCH SCORE: {score:.1f}/{max_score}
{bar} {percentage:.0f}%
Status: {status}
        """
    
    @staticmethod
    def format_analysis_response(
        score: float,
        missing_keywords: list,
        analysis: str,
        suggestions: str
    ) -> str:
        """Format complete analysis response"""
        response = f"""
=== RESUME ANALYSIS REPORT ===

📈 Match Score: {score:.1f}/10

🎯 Missing Skills/Keywords:
"""
        if missing_keywords:
            for i, keyword in enumerate(missing_keywords[:10], 1):
                response += f"  {i}. {keyword}\n"
        else:
            response += "  None identified\n"
        
        response += f"""
📝 Analysis:
{analysis}

💡 Suggestions for Improvement:
{suggestions}
        """
        return response
    
    @staticmethod
    def format_error_response(error: str, context: str = "") -> str:
        """Format error message"""
        response = f"❌ Error: {error}"
        if context:
            response += f"\nContext: {context}"
        return response
    
    @staticmethod
    def format_success_response(message: str) -> str:
        """Format success message"""
        return f"✅ {message}"
