# Resume Analyzer Bot - Telegram AI-Powered Resume Analysis

A sophisticated Telegram bot that analyzes resumes against job descriptions using AI and NLP, provides improvement suggestions, and generates enhanced resumes in PDF format.

## Features

✨ **AI-Powered Analysis**

- Compare resumes with job descriptions using advanced NLP and AI
- Get matching scores (0-10 scale)
- Identify skill gaps and missing keywords
- Receive tailored improvement suggestions

📊 **Comprehensive Scoring**

- TF-IDF based similarity calculation
- Keyword matching against job description
- AI-powered comparative analysis

💡 **Resume Enhancement**

- Generate resume versions tailored to specific job postings
- Incorporate relevant keywords naturally
- Maintain professional structure

📄 **PDF Generation**

- Create ATS-friendly professional PDFs
- Clean, formatted output
- Professional sections: Summary, Skills, Experience, Projects, Education

🤖 **Telegram Integration**

- Seamless file upload support
- Real-time processing updates
- User-friendly command interface
- Interactive conversation flow

## Tech Stack

- **Python 3.8+** - Core language
- **python-telegram-bot** - Telegram API integration
- **OpenAI GPT-3.5/4** - AI analysis (optional)
- **Google Gemini** - Alternative AI provider (optional)
- **pdfplumber** - PDF text extraction
- **reportlab** - PDF generation
- **scikit-learn** - NLP and similarity calculations
- **NLTK** - Natural language processing

## Installation

### Prerequisites

- Python 3.8 or higher
- Telegram account and bot token (from @BotFather)
- OpenAI API key or Google Gemini API key (optional, NLP works without)

### Setup Steps

1. **Clone or navigate to the project**

   ```bash
   cd resume_analyzer_bot
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env with your credentials
   ```

5. **Set up configuration**
   - Edit `config/settings.py` or set environment variables:
     - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
     - `OPENAI_API_KEY`: Your OpenAI API key (optional)
     - `GEMINI_API_KEY`: Your Google Gemini API key (optional)
     - `AI_PROVIDER`: Choose 'openai' or 'gemini' (defaults to 'openai')

## Getting API Keys

### Telegram Bot Token

1. Open Telegram and search for @BotFather
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the provided token

### OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Create new API key
3. Copy and store securely

### Google Gemini API Key

1. Visit https://ai.google.dev/
2. Create API key from Gemini section
3. Copy and store securely

## Running the Bot

### Start the bot

```bash
python bot.py
```

The bot will start polling for messages.

### Optional: Use Webhook instead of Polling

For production, modify `bot.py` to use webhooks:

```python
# Instead of:
await application.run_polling()

# Use:
await application.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path="/telegram",
    webhook_url="https://your-domain.com/telegram"
)
```

## Usage

### Bot Commands

- `/start` - Initialize the bot and begin analysis
- `/analyze` - Start resume analysis workflow
- `/help` - Display help and usage information

### Workflow

1. **Send Job Description**
   - Text input (minimum 50 characters)
   - Paste full job description

2. **Upload Resume**
   - Supported formats: PDF, TXT
   - Maximum file size: 10 MB
   - Bot extracts and processes automatically

3. **Receive Analysis**
   - Matching score (0-10)
   - Missing keywords and skills
   - Strengths identification
   - Improvement suggestions

4. **Generate Enhanced Resume**
   - AI-tailored version
   - Keyword-optimized content
   - Professional structure

5. **Download PDF**
   - ATS-friendly formatting
   - Clean, professional appearance
   - Ready to send to recruiters

## Project Structure

```
resume_analyzer_bot/
├── bot.py                      # Main bot application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration file
│
├── modules/
│   ├── __init__.py
│   ├── extraction.py          # Resume text extraction
│   ├── analysis.py            # AI analysis and scoring
│   ├── enhancement.py         # Resume enhancement
│   └── pdf_generator.py       # PDF generation
│
├── utils/
│   ├── __init__.py
│   └── helpers.py             # Helper functions and utilities
│
└── tmp_uploads/               # Temporary file storage (auto-created)
```

## Module Documentation

### extraction.py

Handles text extraction from various resume formats:

- `extract_from_pdf()` - Extract text from PDF files
- `extract_from_text()` - Read text files
- `clean_text()` - Normalize and clean extracted text

### analysis.py

Performs AI and NLP-based analysis:

- `extract_keywords()` - TF-IDF keyword extraction
- `calculate_nlp_similarity()` - Cosine similarity analysis
- `find_missing_keywords()` - Identify gaps
- `analyze_with_ai()` - AI-powered analysis using OpenAI/Gemini

### enhancement.py

Generates improved resume versions:

- `generate_enhanced_resume()` - Create tailored resume
- AI-powered or rule-based enhancement
- Keyword optimization

### pdf_generator.py

Creates professional PDF resumes:

- `generate_resume_pdf()` - Generate downloadable PDF
- Professional formatting
- Section-based structure

### helpers.py

Utility functions:

- `FileValidator` - File validation and MIME type checking
- `TextProcessor` - Text normalization and processing
- `ResponseFormatter` - Format bot responses

## Configuration Options

Edit `config/settings.py` to customize:

| Setting                | Default  | Description                       |
| ---------------------- | -------- | --------------------------------- |
| `AI_PROVIDER`          | "openai" | AI provider: 'openai' or 'gemini' |
| `MAX_FILE_SIZE`        | 10 MB    | Maximum resume file size          |
| `SIMILARITY_THRESHOLD` | 0.3      | Minimum similarity score          |
| `MAX_MATCHING_SCORE`   | 10       | Maximum possible score            |
| `PROCESSING_TIMEOUT`   | 60       | Processing timeout in seconds     |

## Error Handling

The bot handles:

- Invalid file formats
- Oversized files
- Extraction errors
- API failures (graceful degradation)
- Network issues

## Performance Considerations

- **File Extraction**: ~1-3 seconds for typical resumes
- **NLP Analysis**: ~2-5 seconds
- **AI Analysis**: ~5-15 seconds (depends on API response time)
- **PDF Generation**: ~1-2 seconds

## Limitations

- PDF files must contain extractable text (scanned PDFs may not work)
- Very long documents may be truncated
- AI responses limited by API rate limits
- Telegram file size limit: 20 MB

## Troubleshooting

### "Bot not responding"

- Check TELEGRAM_BOT_TOKEN in config
- Verify internet connection
- Check for firewall issues

### "API key invalid"

- Verify API key is correctly entered
- Check key hasn't expired
- Ensure correct provider is selected

### "PDF generation fails"

- Check write permissions in tmp_uploads directory
- Verify reportlab is installed correctly
- Check disk space availability

### "No text extracted from PDF"

- Ensure PDF is not scanned image
- Try converting PDF to text first
- Check PDF is not corrupted

## Security Notes

⚠️ **Important:**

- Never commit `.env` file with real credentials
- Use environment variable substitution in production
- Rotate API keys periodically
- Implement user rate limiting for production
- Add authentication for production deployment

## Future Enhancements

- [ ] Multi-language support
- [ ] LinkedIn profile integration
- [ ] Salary expectations analysis
- [ ] Interview question suggestions
- [ ] Job market trend analysis
- [ ] Bulk resume processing
- [ ] Resume template library
- [ ] Cover letter generation

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with improvements

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions:

- Create an issue in the repository
- Contact the development team
- Check the FAQ section

## Changelog

### Version 1.0.0 (Initial Release)

- Core resume analysis functionality
- AI-powered matching and scoring
- Enhanced resume generation
- PDF export capability
- Full Telegram integration

---

**Happy Analyzing! 🚀**

Built with ❤️ for job seekers and recruiters.
