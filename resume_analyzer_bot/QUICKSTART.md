# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Python and Dependencies

```bash
# Windows/macOS/Linux
python -m pip install --upgrade pip

# Navigate to project directory
cd resume_analyzer_bot

# Run setup script
python setup.py
```

### Step 2: Get Your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name and username for your bot
4. Copy the token provided (looks like: `123456789:ABCdefGHIjklmnoPQRstuvWXYZ`)

### Step 3: Get an AI API Key (Optional but Recommended)

**Choose OpenAI:**

1. Visit https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key and store it safely

**OR Choose Google Gemini:**

1. Visit https://ai.google.dev/
2. Click "Get API key"
3. Create and copy your Gemini API key

### Step 4: Configure the Bot

```bash
# Edit .env file (Windows CMD/PowerShell)
notepad .env

# Or use any text editor
# macOS/Linux
nano .env
```

Fill in:

```
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
AI_PROVIDER=openai
```

### Step 5: Start the Bot

```bash
# Activate virtual environment (if on Windows)
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# Run bot
python bot.py
```

You should see:

```
🚀 Resume Analyzer Bot is starting...
```

## Testing the Bot

### Start Telegram Bot

1. Open Telegram and search for your bot username
2. Send `/start`
3. Bot responds with welcome message

### Test Workflow

1. **Send Job Description**: Copy the text from `examples/sample_job_description.txt`
2. **Upload Resume**: Use `examples/sample_resume.txt` (save as file or upload as document)
3. **Review Analysis**: Bot will provide:
   - Matching score
   - Missing skills
   - Improvement suggestions
4. **Generate Enhanced Resume**: Click the button or type "Generate Enhanced Resume"
5. **Download PDF**: Click the button or type "Download PDF"

## Example Test Data

We've provided sample files in the `examples/` directory:

- `sample_resume.txt` - Example resume for testing
- `sample_job_description.txt` - Example job description

Use these to test the bot's functionality.

## Troubleshooting

### Bot not starting

```
Error: TELEGRAM_BOT_TOKEN not set in config
```

**Solution**: Make sure you've added your token to `.env` file

### No API responses

```
Error: Connection timeout
```

**Solution**:

- Check internet connection
- Verify firewall isn't blocking Telegram
- Restart the bot

### PDF generation fails

```
Error: Permission denied for tmp_uploads
```

**Solution**:

```bash
# Create the missing directory
mkdir tmp_uploads output_resumes
```

### Python modules not found

```
ModuleNotFoundError: No module named 'telegram'
```

**Solution**: Make sure virtual environment is activated:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

## Commands Reference

| Command    | Purpose                               |
| ---------- | ------------------------------------- |
| `/start`   | Initialize bot and begin new analysis |
| `/analyze` | Start the analysis workflow           |
| `/help`    | Show help and commands                |

## Files Explanation

```
resume_analyzer_bot/
├── bot.py                 # Main bot - RUN THIS
├── setup.py              # Installation setup
├── requirements.txt      # All dependencies
├── .env                  # Your credentials (create from .env.example)
├── config/settings.py    # Bot configuration
├── modules/              # Core functionality
│   ├── extraction.py    # Extract text from files
│   ├── analysis.py      # Analyze and score
│   ├── enhancement.py   # Improve resume
│   └── pdf_generator.py # Create PDF
├── utils/helpers.py      # Helper functions
├── examples/             # Sample files for testing
└── tmp_uploads/          # Uploaded files (auto-created)
```

## Using Without AI API (Basic Mode)

If you don't have an AI API key, the bot still works using NLP:

1. Leave `OPENAI_API_KEY` empty in `.env`
2. Bot will use built-in NLP analysis instead
3. Scoring and analysis still work, just less detailed

## Environment Variables

| Variable             | Required | Example              |
| -------------------- | -------- | -------------------- |
| `TELEGRAM_BOT_TOKEN` | Yes      | `123456:ABCdef...`   |
| `OPENAI_API_KEY`     | No       | `sk-abc123...`       |
| `GEMINI_API_KEY`     | No       | `AIza...`            |
| `AI_PROVIDER`        | No       | `openai` or `gemini` |
| `MAX_FILE_SIZE`      | No       | `10485760` (10 MB)   |

## Performance Tips

1. **Faster Processing**: Use OpenAI API for better analysis
2. **Lower Costs**: Use NLP-only mode (no API key needed)
3. **Resume Quality**: Provide clear, well-formatted resumes
4. **File Format**: Use TXT files instead of PDFs when possible

## File Format Support

| Format | Status       | Notes                      |
| ------ | ------------ | -------------------------- |
| PDF    | ✅ Supported | Must have extractable text |
| TXT    | ✅ Supported | Preferred format           |
| DOCX   | ⚠️ Limited   | Requires text extraction   |

## Next Steps

- [ ] Customize `config/settings.py` for your needs
- [ ] Test with sample files in `examples/`
- [ ] Add more AI providers if desired
- [ ] Deploy to production (VPS, AWS Lambda, Heroku)

## Support & Help

**In the bot**: Send `/help`

**GitHub Issues**: Report bugs or request features

**Community**: Join discussions about improvements

## Deployment Options

### Option 1: Local Machine

- Simplest for testing
- Bot runs in terminal
- Machine must stay online

### Option 2: VPS/Cloud Server

- AWS EC2, DigitalOcean, Linode
- Use systemd to run as service
- Domain-based webhook support

### Option 3: Serverless (AWS Lambda)

- Cost-effective
- Auto-scaling
- Webhook-based (not polling)

### Option 4: Docker Container

```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
```

## Estimated Costs

**Free Tier:**

- Telegram: Always free
- NLP-only mode: Free

**With AI:**

- OpenAI (GPT-3.5): ~$0.01-0.10 per request
- Google Gemini: Free tier available

## Common Questions

**Q: Can I run on my phone?**
A: Not directly, but you can run on a cheap VPS ($3-5/month)

**Q: Is my data private?**
A: Data is sent to AI providers as per their policies

**Q: Can I customize the PDF format?**
A: Yes, edit `modules/pdf_generator.py`

**Q: How many users can the bot handle?**
A: Unlimited with Telegram, depends on your server resources

---

**Ready to use?** Start with Step 1 above! 🚀
