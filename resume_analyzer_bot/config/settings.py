# Bot Configuration Settings

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# AI API Configuration
# Choose which AI provider to use: 'openai' or 'gemini'
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

# File Settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))
ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx'}
TEMP_FILES_DIR = os.getenv("TEMP_FILES_DIR", "tmp_uploads")

# Resume Analysis Settings
MIN_MATCHING_SCORE = int(os.getenv("MIN_MATCHING_SCORE", 0))
MAX_MATCHING_SCORE = int(os.getenv("MAX_MATCHING_SCORE", 10))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.3))

# PDF Generation Settings
PDF_MARGIN_SIZE = float(os.getenv("PDF_MARGIN_SIZE", 0.5))
PDF_FONT_NAME = os.getenv("PDF_FONT_NAME", "Helvetica")
PDF_FONT_SIZE = int(os.getenv("PDF_FONT_SIZE", 10))
PDF_TITLE_SIZE = 14
PDF_SECTION_SIZE = 12

# Performance Settings
PROCESSING_TIMEOUT = 60  # seconds
MAX_RETRIES = 3
