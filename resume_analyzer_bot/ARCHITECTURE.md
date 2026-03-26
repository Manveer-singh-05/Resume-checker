# Architecture & Technical Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT CLIENT                      │
│              (User sends commands and files)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Telegram Bot API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   MAIN BOT APPLICATION                      │
│                      (bot.py)                               │
│  - Conversation State Management                            │
│  - File Upload Handling                                     │
│  - User Session Management                                  │
└────────┬────────────────────────────────────────────────────┘
         │
    ┌────┴────┬──────────────────┬────────────────┬──────────┐
    │          │                  │                │          │
    ▼          ▼                  ▼                ▼          ▼
┌────────┐ ┌────────┐       ┌─────────┐    ┌──────────┐ ┌────────┐
│Extract │ │Analyze │       │Enhance  │    │Generate  │ │Helpers │
│ Module │ │ Module │       │ Module  │    │PDF Module│ │ Module │
└────────┘ └────────┘       └─────────┘    └──────────┘ └────────┘
    │          │                  │                │
    │          ├──────────────────┼────────────────┤
    │          │                  │                │
    ▼          ▼                  ▼                ▼
  ┌───────────────────────────────────────────────────────┐
  │           AI/NLP Processing Layer                    │
  │  ┌──────────────┐          ┌──────────────────────┐ │
  │  │NLP Similarity│          │ AI API Integration   │ │
  │  │(scikit-learn)│──and/or──│ (OpenAI/Gemini API) │ │
  │  └──────────────┘          └──────────────────────┘ │
  └───────────────────────────────────────────────────────┘
    │          │                  │
    └──────────┴──────────────────┘
                 │
    ┌────────────┴──────────────┐
    │                           │
    ▼                           ▼
┌──────────┐           ┌──────────────────┐
│TMP Files │           │Output PDFs       │
│(Uploads) │           │(Enhanced Resumes)│
└──────────┘           └──────────────────┘
```

---

## Data Flow

### Resume Analysis Flow

```
User Upload
    │
    ├─→ Validate File
    │   ├─ Check extension
    │   ├─ Check file size
    │   └─ Check content
    │
    ├─→ Extract Text
    │   ├─ PDF: Use pdfplumber
    │   ├─ TXT: Read file
    │   └─ Clean text
    │
    ├─→ NLP Analysis
    │   ├─ TF-IDF keyword extraction
    │   ├─ Cosine similarity
    │   └─ Find missing keywords
    │
    ├─→ AI Analysis (Optional)
    │   ├─ Send to OpenAI/Gemini
    │   ├─ Receive scoring
    │   └─ Parse response
    │
    ├─→ Generate Report
    │   ├─ Format analysis
    │   ├─ Create suggestions
    │   └─ Send to user
    │
    └─→ Store Session Data
        └─ Keep for enhancement
```

### Resume Enhancement & PDF Generation

```
Generate Enhancement Request
    │
    ├─→ Load Session Data
    │   ├─ Resume text
    │   └─ Job description
    │
    ├─→ Enhancement Process
    │   ├─ AI enhancement (if available)
    │   │   ├─ Send prompt to API
    │   │   ├─ Receive enhanced content
    │   │   └─ Parse JSON response
    │   │
    │   └─ Or Rule-based enhancement
    │       ├─ Parse sections
    │       ├─ Extract job keywords
    │       ├─ Inject keywords naturally
    │       └─ Return structured data
    │
    ├─→ PDF Generation
    │   ├─ Create ReportLab document
    │   ├─ Format sections
    │   ├─ Apply styling
    │   ├─ Generate PDF
    │   └─ Save to file
    │
    ├─→ Upload to Telegram
    │   ├─ Send as document
    │   └─ Provide download link
    │
    └─→ Cleanup Temp Files
        └─ Delete after 24 hours
```

---

## Module Details

### 1. Extraction Module (`extraction.py`)

**Responsibility**: Extract text from various file formats

**Key Classes**:

```python
class ResumeExtractor:
    - extract_from_pdf()          # PDF text extraction
    - extract_from_text()         # TXT file reading
    - extract_from_file()         # Auto-detect + extract
    - clean_text()                # Normalize text
```

**Technologies**:

- `pdfplumber`: PDF parsing
- `PyPDF2`: PDF manipulation (fallback)

**Error Handling**:

- Corrupted PDFs
- Empty files
- Encoding issues
- Large files

---

### 2. Analysis Module (`analysis.py`)

**Responsibility**: Perform NLP and AI-based resume analysis

**Key Classes**:

```python
class AIAnalyzer:
    - extract_keywords()          # TF-IDF extraction
    - calculate_nlp_similarity()  # Cosine similarity
    - find_missing_keywords()     # Gap analysis
    - analyze_with_ai()           # AI-powered analysis
    - _analyze_with_openai()      # OpenAI implementation
    - _analyze_with_gemini()      # Gemini implementation
    - _analyze_with_nlp()         # NLP-only fallback
```

**Technologies**:

- `scikit-learn`: TF-IDF vectorization, similarity
- `NLTK`: Natural language processing
- `OpenAI API`: GPT-based analysis
- `Google Gemini API`: Alternative AI

**Scoring Algorithm**:

```python
score = min(10, similarity * 12)  # Normalize to 0-10
```

---

### 3. Enhancement Module (`enhancement.py`)

**Responsibility**: Generate improved resume versions

**Key Classes**:

```python
class ResumeEnhancer:
    - generate_enhanced_resume()  # Main enhancement
    - _enhance_with_ai()          # AI enhancement
    - _enhance_with_rules()       # Rule-based enhancement
    - _parse_resume_sections()    # Section parsing
    - _extract_job_keywords()     # Keyword extraction
    - _enhance_summary()          # Summary improvement
    - _enhance_skills()           # Skills enhancement
    - _enhance_experience()       # Experience improvement
```

**Enhancement Strategy**:

1. Parse resume into sections
2. Extract job keywords
3. Inject keywords naturally
4. Maintain professional structure
5. Use AI if available for quality

---

### 4. PDF Generator Module (`pdf_generator.py`)

**Responsibility**: Create professional ATS-friendly PDFs

**Key Classes**:

```python
class PDFGenerator:
    - generate_resume_pdf()       # Main PDF generation
    - _get_custom_styles()        # ReportLab styling
    - _format_contact_info()      # Contact formatting
    - cleanup_temp_files()        # File cleanup
```

**Features**:

- Professional formatting
- Section-based structure
- Contact information header
- ATS-friendly design
- Auto-cleanup of old files

**ReportLab Components**:

- `SimpleDocTemplate`: Document structure
- `Paragraph`: Text with styling
- `Spacer`: Layout spacing
- `ParagraphStyle`: Custom formatting

---

### 5. Helpers Module (`helpers.py`)

**Responsibility**: Utility functions and validation

**Key Classes**:

```python
class FileValidator:
    - validate_file()             # File validation
    - get_mime_type()             # MIME type detection

class TextProcessor:
    - normalize_text()            # Text normalization
    - truncate_text()             # Length limiting
    - count_words()               # Word count
    - count_lines()               # Line count

class ResponseFormatter:
    - format_score_response()     # Score display
    - format_analysis_response()  # Analysis formatting
    - format_error_response()     # Error messages
    - format_success_response()   # Success messages
```

---

## Conversation State Management

### States

```python
AWAITING_JOB_DESC = 0    # Waiting for job description
AWAITING_RESUME    = 1    # Waiting for resume upload
PROCESSING         = 2    # Analyzing resume
```

### State Transitions

```
START (AWAITING_JOB_DESC)
  ↓ User sends job description
AWAITING_RESUME
  ↓ User uploads resume
PROCESSING
  ↓ Analysis complete
MENU (can generate enhanced resume or PDF)
  ↓ User choice
  ├→ Generate Enhanced Resume → MENU
  ├→ Generate PDF → MENU
  └→ New Analysis → START
```

### User Session Storage

```python
self.user_sessions[user_id] = {
    'job_description': str,      # Original job description
    'resume_path': str,          # Path to uploaded resume
    'resume_text': str,          # Extracted resume text
    'analysis': dict,            # Analysis results
    'enhanced_resume': dict      # Enhanced resume data
}
```

---

## API Integration

### OpenAI Integration

```python
Response Format {
    "score": 0-10,
    "strengths": "...",
    "missing_items": ["skill1", "skill2"],
    "suggestions": "..."
}
```

### Gemini Integration

```python
Response Format {
    "score": 0-10,
    "strengths": "...",
    "missing_items": ["skill1", "skill2"],
    "suggestions": "..."
}
```

### Fallback: NLP Only

- No API key required
- Use sklearn TF-IDF
- Basic similarity + keyword matching
- No quality loss, just less sophisticated

---

## Error Handling

### File Upload Errors

```
❌ File too large              → Download proper file
❌ Unsupported format          → Supported: PDF, TXT
❌ Empty or corrupted file     → Use valid resume
❌ Encoding issue              → Re-save in UTF-8
```

### API Errors

```
❌ API key invalid             → Check .env settings
❌ Rate limit exceeded         → Wait and retry
❌ Network timeout             → Check connection
❌ Invalid response format     → Try again
```

### Processing Errors

```
❌ Text extraction failed      → Ensure valid PDF
❌ Analysis timeout            → File too large
❌ PDF generation error        → Disk space issue
```

---

## Performance Metrics

### Processing Times (Average)

```
PDF Text Extraction:     1-3 seconds
TXT Text Extraction:     <1 second
NLP Analysis:            2-5 seconds
AI Analysis (OpenAI):    5-15 seconds
AI Analysis (Gemini):    5-15 seconds
PDF Generation:          1-2 seconds
Total Workflow:          10-40 seconds
```

### Memory Usage

```
Idle:                    ~50 MB
Processing file:         ~100-200 MB
Multiple users:          ~20 MB per user
```

### File Size Limits

```
Resume:                  10 MB (configurable)
Job Description:         Unlimited (truncated)
Generated PDF:           0.5-2 MB
```

---

## Security Considerations

### Data Protection

1. **File Uploads**: Validated before processing
2. **Temporary Files**: Auto-cleaned after 24 hours
3. **User Data**: Stored in memory only (no persistence)
4. **API Keys**: Never logged or exposed

### Rate Limiting (Recommended)

```python
from telegram.ext import Application

# Configure in production
app.add_handler(MessageHandler(
    filters.TEXT,
    handle_with_rate_limit
))
```

### Input Validation

```python
# Always validate:
- File type
- File size
- Text length
- JSON parsing
```

---

## Scalability

### Horizontal Scaling (Multiple Instances)

1. Use Redis for state sharing
2. Load balancer for traffic distribution
3. Shared file storage (S3, NFS)

### Vertical Scaling (Single Instance)

1. Database for user sessions
2. Caching (Redis)
3. Async processing (Celery)

---

## Testing Strategy

### Unit Tests

```python
test_text_extraction()
test_keyword_extraction()
test_nlp_similarity()
test_missing_keywords()
test_resume_enhancement()
test_pdf_generation()
```

### Integration Tests

```python
test_full_workflow()
test_api_integration()
test_file_upload_handling()
```

### Performance Tests

```python
test_processing_speed()
test_memory_usage()
test_concurrent_users()
```

---

## Deployment Checklist

- [ ] Set environment variables
- [ ] Test with sample files
- [ ] Configure API keys
- [ ] Setup systemd service
- [ ] Configure logging
- [ ] Setup monitoring
- [ ] Enable SSL/TLS
- [ ] Configure backups
- [ ] Test error handling
- [ ] Document deployment
- [ ] Plan disaster recovery

---

## Future Enhancements

1. **Database Integration**
   - User profiles
   - Resume history
   - Application tracking

2. **Advanced Features**
   - LinkedIn profile analysis
   - Salary negotiation tips
   - Interview question generation

3. **Multi-language Support**
   - Auto-detect language
   - Translation API integration
   - Localized responses

4. **Machine Learning**
   - Success prediction model
   - Job recommendation engine
   - Career path analysis

5. **Integration**
   - Email integration
   - Slack bot
   - Web dashboard
   - Mobile app

---

## References

- Telegram Bot API: https://core.telegram.org/bots/api
- Python Telegram Bot: https://python-telegram-bot.readthedocs.io/
- ReportLab: https://www.reportlab.com/docs/reportlab-userguide.pdf
- scikit-learn: https://scikit-learn.org/stable/documentation.html
- OpenAI API: https://platform.openai.com/docs/

---

## License & Support

This project is open source. For support and questions, see README.md.
