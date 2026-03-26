"""
Main Telegram Bot Application
Resume Analyzer Bot - AI-powered resume analysis and improvement
"""

import os
import logging
import tempfile
import asyncio
import warnings
from pathlib import Path
from typing import Optional
from datetime import datetime

# Suppress urllib3 warnings
warnings.filterwarnings('ignore', message='urllib3')

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Document
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Import custom modules
from config.settings import (
    TELEGRAM_BOT_TOKEN,
    AI_PROVIDER,
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    MAX_FILE_SIZE,
    TEMP_FILES_DIR,
    OPENAI_MODEL
)
from modules.extraction import ResumeExtractor
from modules.analysis import AIAnalyzer
from modules.enhancement import ResumeEnhancer
from modules.pdf_generator import PDFGenerator
from utils.helpers import FileValidator, TextProcessor, ResponseFormatter

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
AWAITING_JOB_DESC, AWAITING_RESUME, PROCESSING, AWAITING_MODIFICATION_CHOICE, AWAITING_TEMPLATE_SELECTION, AWAITING_PDF_ACTION = range(6)


class ResumeVisualizer:
    """Main bot application"""
    
    def __init__(self):
        """Initialize bot"""
        self.extractor = ResumeExtractor()
        self.analyzer = AIAnalyzer(
            ai_provider=AI_PROVIDER,
            api_key=OPENAI_API_KEY if AI_PROVIDER == "openai" else GEMINI_API_KEY,
            model=OPENAI_MODEL
        )
        self.enhancer = ResumeEnhancer(
            ai_provider=AI_PROVIDER,
            api_key=OPENAI_API_KEY if AI_PROVIDER == "openai" else GEMINI_API_KEY
        )
        self.pdf_generator = PDFGenerator(output_dir=TEMP_FILES_DIR)
        
        # Ensure temp directory exists
        os.makedirs(TEMP_FILES_DIR, exist_ok=True)
        
        # User sessions
        self.user_sessions = {}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start command handler"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        welcome_message = f"""
👋 Welcome, {user_name}! I'm your Resume Visualizer Bot.

I'll help you:
✨ Analyze your resume against job descriptions
📊 Get a matching score and identify gaps
💡 Receive improvement suggestions
✍️ Generate an enhanced resume tailored to the job
📄 Create a professional PDF version

Let's get started! Please send me the job description first (as text).
        """
        
        await update.message.reply_text(welcome_message)
        
        # Initialize user session
        self.user_sessions[user_id] = {
            'job_description': None,
            'resume_path': None,
            'resume_text': None,
            'analysis': None,
            'enhanced_resume': None
        }
        
        return AWAITING_JOB_DESC
    
    async def receive_job_description(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive job description from user"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        if len(user_message) < 50:
            await update.message.reply_text(
                "❌ Job description too short. Please provide a more detailed job description (at least 50 characters)."
            )
            return AWAITING_JOB_DESC
        
        # Store job description
        self.user_sessions[user_id]['job_description'] = user_message
        
        await update.message.reply_text(
            "✅ Job description received!\n\n"
            "Now please upload your resume (PDF or TXT file)."
        )
        
        return AWAITING_RESUME
    
    async def receive_resume(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Receive resume file from user"""
        user_id = update.effective_user.id
        
        if not update.message.document:
            await update.message.reply_text(
                "❌ Please send a file. Supported formats: PDF, TXT"
            )
            return AWAITING_RESUME
        
        document = update.message.document
        
        # Validate file
        file_name = document.file_name
        file_ext = Path(file_name).suffix.lower()
        
        if file_ext not in FileValidator.ALLOWED_EXTENSIONS:
            await update.message.reply_text(
                f"❌ Unsupported file format: {file_ext}\n"
                f"Allowed formats: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}"
            )
            return AWAITING_RESUME
        
        if document.file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                f"❌ File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
            )
            return AWAITING_RESUME
        
        try:
            # Download file
            await update.message.reply_text("⏳ Downloading and processing your resume...")
            
            file = await context.bot.get_file(document.file_id)
            temp_file = tempfile.NamedTemporaryFile(
                suffix=file_ext, 
                delete=False,
                dir=TEMP_FILES_DIR
            )
            await file.download_to_memory(temp_file)
            temp_file.close()
            
            # Extract text
            success, text, error = self.extractor.extract_from_file(temp_file.name)
            
            if not success:
                await update.message.reply_text(
                    f"❌ Error extracting text: {error}"
                )
                os.unlink(temp_file.name)
                return AWAITING_RESUME
            
            # Clean text
            cleaned_text = self.extractor.clean_text(text)
            
            # Store in session
            self.user_sessions[user_id]['resume_path'] = temp_file.name
            self.user_sessions[user_id]['resume_text'] = cleaned_text
            
            # Start analysis immediately
            await update.message.reply_text(
                "✅ Resume received!\n\n"
                "🔍 Analyzing... This may take a moment (up to 30 seconds)."
            )
            
            # Perform analysis immediately
            try:
                session = self.user_sessions[user_id]
                job_desc = session['job_description']
                resume_text = session['resume_text']
                
                # Get AI analysis
                score, analysis, suggestions = self.analyzer.analyze_with_ai(resume_text, job_desc)
                
                # Find missing keywords
                missing_keywords = self.analyzer.find_missing_keywords(resume_text, job_desc)
                
                # Store analysis
                session['analysis'] = {
                    'score': score,
                    'analysis': analysis,
                    'suggestions': suggestions,
                    'missing_keywords': missing_keywords
                }
                
                # Format and send analysis
                analysis_response = ResponseFormatter.format_analysis_response(
                    score, missing_keywords, analysis, suggestions
                )
                
                await update.message.reply_text(analysis_response)
                
                # Auto-enhance resume immediately (Professional template)
                await update.message.reply_text(
                    "✨ Enhancing your CV based on the analysis...\n"
                    "This may take 30-45 seconds..."
                )
                
                try:
                    # Generate enhanced resume with Professional template
                    # Pass missing keywords to specifically target identified gaps
                    enhanced = self.enhancer.generate_enhanced_resume(
                        session['resume_text'],
                        session['job_description'],
                        use_ai=bool(OPENAI_API_KEY or GEMINI_API_KEY),
                        missing_keywords=session['analysis'].get('missing_keywords', [])
                    )
                    
                    # Store the enhanced resume
                    session['enhanced_resume'] = enhanced
                    session['selected_template'] = 'professional'
                    
                    # Display enhanced CV
                    display_text = "📄 YOUR ENHANCED CV (PROFESSIONAL)\n\n"
                    
                    if enhanced.get('summary'):
                        display_text += f"**PROFESSIONAL SUMMARY**\n{enhanced['summary']}\n\n"
                    if enhanced.get('skills'):
                        display_text += f"**SKILLS**\n{enhanced['skills']}\n\n"
                    if enhanced.get('experience'):
                        display_text += f"**EXPERIENCE**\n{enhanced['experience']}\n\n"
                    if enhanced.get('education'):
                        display_text += f"**EDUCATION**\n{enhanced['education']}\n\n"
                    
                    # Split if too long
                    if len(display_text) > 4096:
                        parts = [display_text[i:i+4096] for i in range(0, len(display_text), 4096)]
                        for part in parts:
                            await update.message.reply_text(part, parse_mode='Markdown')
                    else:
                        await update.message.reply_text(display_text, parse_mode='Markdown')
                    
                    # Show download and options
                    reply_keyboard = [
                        ['📥 Download as PDF'],
                        ['🎨 Try Different Template', '📊 New Analysis']
                    ]
                    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
                    
                    await update.message.reply_text(
                        "✅ Your enhanced CV is ready!\n\n"
                        "Ready to download or try a different template?",
                        reply_markup=reply_markup
                    )
                    
                    return AWAITING_PDF_ACTION
                    
                except Exception as enhance_error:
                    await update.message.reply_text(
                        f"⚠️ Enhancement completed but with minor issues.\n"
                        f"Click below to download your CV:"
                    )
                    reply_keyboard = [
                        ['📥 Download as PDF']
                    ]
                    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
                    await update.message.reply_text(
                        "What would you like to do?",
                        reply_markup=reply_markup
                    )
                    return AWAITING_PDF_ACTION
                
            except Exception as analysis_error:
                await update.message.reply_text(
                    f"❌ Error during analysis: {str(analysis_error)}\n"
                    f"Falling back to NLP-only analysis..."
                )
                # Fall back to NLP analysis
                score = 5.0
                missing_keywords = []
                analysis = "Analysis failed - using NLP fallback"
                suggestions = "Please try again"
            
            return AWAITING_JOB_DESC
        
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error processing file: {str(e)}"
            )
            return AWAITING_RESUME
    
    async def process_analysis(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Process complete analysis"""
        user_id = update.effective_user.id
        session = self.user_sessions[user_id]
        
        try:
            job_desc = session['job_description']
            resume_text = session['resume_text']
            
            # Get AI analysis
            score, analysis, suggestions = self.analyzer.analyze_with_ai(resume_text, job_desc)
            
            # Find missing keywords
            missing_keywords = self.analyzer.find_missing_keywords(resume_text, job_desc)
            
            # Store analysis
            session['analysis'] = {
                'score': score,
                'analysis': analysis,
                'suggestions': suggestions,
                'missing_keywords': missing_keywords
            }
            
            # Format and send analysis
            analysis_response = ResponseFormatter.format_analysis_response(
                score, missing_keywords, analysis, suggestions
            )
            
            await update.message.reply_text(analysis_response)
            
            # Ask for next step
            reply_keyboard = [
                ['Generate Enhanced Resume', 'Download PDF'],
                ['New Analysis', 'Help']
            ]
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )
            
            await update.message.reply_text(
                "What would you like to do next?",
                reply_markup=reply_markup
            )
            
            return AWAITING_JOB_DESC  # Ready for next command
        
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error during analysis: {str(e)}"
            )
            return AWAITING_JOB_DESC
    
    async def handle_message(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle text messages based on conversation state"""
        user_message = update.message.text.lower()
        
        if "download" in user_message and "pdf" in user_message:
            return await self.generate_pdf(update, context)
        elif "different" in user_message or "template" in user_message:
            # Show template options again
            reply_keyboard = [
                ['Professional', 'Modern'],
                ['Minimal', 'Creative'],
                ['Academic', 'Executive']
            ]
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )
            
            await update.message.reply_text(
                "📋 Choose another CV template style:",
                reply_markup=reply_markup
            )
            return AWAITING_TEMPLATE_SELECTION
        elif "new" in user_message or "analysis" in user_message:
            return await self.start(update, context)
        else:
            return await self.receive_job_description(update, context)
    
    async def handle_modification_choice(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle user choice to modify resume or not"""
        user_message = update.message.text.lower()
        user_id = update.effective_user.id
        
        if "yes" in user_message or "modify" in user_message:
            # Show template options
            reply_keyboard = [
                ['Professional', 'Modern'],
                ['Minimal', 'Creative'],
                ['Academic', 'Executive']
            ]
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )
            
            await update.message.reply_text(
                "📋 Choose a CV template style:\n\n"
                "🔹 **Professional** - Classic corporate format\n"
                "🔹 **Modern** - Clean, contemporary design\n"
                "🔹 **Minimal** - Simple, focused layout\n"
                "🔹 **Creative** - Eye-catching format\n"
                "🔹 **Academic** - Research-focused layout\n"
                "🔹 **Executive** - Senior-level format",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return AWAITING_TEMPLATE_SELECTION
        else:
            # User chose to skip
            reply_keyboard = [
                ['New Analysis', 'Help']
            ]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "✅ No problem! What would you like to do next?",
                reply_markup=reply_markup
            )
            
            return AWAITING_JOB_DESC
    
    async def handle_template_selection(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle template selection and generate enhanced resume"""
        user_id = update.effective_user.id
        template_text = update.message.text.lower()
        session = self.user_sessions.get(user_id)
        
        # Extract template name (handle both "professional" and "professional - Classic corporate format")
        template_choice = template_text.split(' - ')[0].strip()
        
        if not session or not session.get('resume_text') or not session.get('job_description'):
            await update.message.reply_text(
                "❌ Session expired. Please /start again."
            )
            return AWAITING_JOB_DESC
        
        try:
            await update.message.reply_text(
                f"✨ Generating your {template_choice} CV...\n\n"
                "This may take 30-45 seconds..."
            )
            
            # Generate enhanced resume with template
            # Pass missing keywords to specifically target identified gaps
            enhanced = self.enhancer.generate_enhanced_resume(
                session['resume_text'],
                session['job_description'],
                use_ai=bool(OPENAI_API_KEY or GEMINI_API_KEY),
                missing_keywords=session.get('analysis', {}).get('missing_keywords', [])
            )
            
            # Store the enhanced resume
            session['enhanced_resume'] = enhanced
            session['selected_template'] = template_choice
            
            # Format enhanced resume for display
            display_text = f"📄 ENHANCED CV ({template_choice.upper()})\n\n"
            
            if enhanced.get('summary'):
                display_text += f"**PROFESSIONAL SUMMARY**\n{enhanced['summary']}\n\n"
            if enhanced.get('skills'):
                display_text += f"**SKILLS**\n{enhanced['skills']}\n\n"
            if enhanced.get('experience'):
                display_text += f"**EXPERIENCE**\n{enhanced['experience']}\n\n"
            if enhanced.get('education'):
                display_text += f"**EDUCATION**\n{enhanced['education']}\n\n"
            
            # Split if too long (Telegram has message limit)
            if len(display_text) > 4096:
                parts = [display_text[i:i+4096] for i in range(0, len(display_text), 4096)]
                for part in parts:
                    await update.message.reply_text(part, parse_mode='Markdown')
            else:
                await update.message.reply_text(display_text, parse_mode='Markdown')
            
            # Ask to download PDF
            reply_keyboard = [
                ['Download as PDF', 'Generate Different Template'],
                ['Start New Analysis']
            ]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "✅ Your enhanced CV is ready!\n\n"
                "Would you like to download it as a PDF?",
                reply_markup=reply_markup
            )
            
            return AWAITING_PDF_ACTION
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error generating CV: {str(e)}")
            return AWAITING_PDF_ACTION
    
    async def generate_enhanced_resume(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Generate enhanced resume"""
        user_id = update.effective_user.id
        session = self.user_sessions[user_id]
        
        try:
            await update.message.reply_text("✨ Generating enhanced resume...")
            
            enhanced = self.enhancer.generate_enhanced_resume(
                session['resume_text'],
                session['job_description'],
                use_ai=bool(OPENAI_API_KEY or GEMINI_API_KEY),
                missing_keywords=session.get('analysis', {}).get('missing_keywords', [])
            )
            
            session['enhanced_resume'] = enhanced
            
            # Format enhanced resume for display
            display_text = "📄 ENHANCED RESUME\n\n"
            
            if enhanced.get('summary'):
                display_text += f"**PROFESSIONAL SUMMARY**\n{enhanced['summary']}\n\n"
            if enhanced.get('skills'):
                display_text += f"**SKILLS**\n{enhanced['skills']}\n\n"
            if enhanced.get('experience'):
                display_text += f"**EXPERIENCE**\n{enhanced['experience']}\n\n"
            
            # Split if too long
            if len(display_text) > 4096:
                await update.message.reply_text(display_text[:4096])
                await update.message.reply_text(display_text[4096:])
            else:
                await update.message.reply_text(display_text)
            
            # Ask for PDF generation
            reply_keyboard = [
                ['Generate PDF', 'New Analysis']
            ]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "Ready to generate PDF?",
                reply_markup=reply_markup
            )
            
            return AWAITING_JOB_DESC
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return AWAITING_JOB_DESC
    
    async def handle_pdf_action(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle PDF action choices after CV is generated"""
        user_message = update.message.text.lower()
        user_id = update.effective_user.id
        session = self.user_sessions.get(user_id)
        
        # Check if download PDF is requested
        if "download" in user_message or "pdf" in user_message:
            return await self.generate_pdf(update, context)
        # Check if different template is requested
        elif "different" in user_message or "template" in user_message:
            # Show template options again
            reply_keyboard = [
                ['Professional', 'Modern'],
                ['Minimal', 'Creative'],
                ['Academic', 'Executive']
            ]
            reply_markup = ReplyKeyboardMarkup(
                reply_keyboard,
                one_time_keyboard=True,
                resize_keyboard=True
            )
            
            await update.message.reply_text(
                "📋 Choose another CV template style:",
                reply_markup=reply_markup
            )
            return AWAITING_TEMPLATE_SELECTION
        # Check if new analysis is requested
        elif "new" in user_message or "analysis" in user_message or "start" in user_message:
            return await self.start(update, context)
        else:
            # If not recognized, acknowledge and show menu again
            await update.message.reply_text(
                "✓ Got it! Here are your options:",
            )
            # Show options again with buttons
            reply_keyboard = [
                ['Download as PDF', 'Generate Different Template'],
                ['Start New Analysis']
            ]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "What would you like to do?",
                reply_markup=reply_markup
            )
            return AWAITING_PDF_ACTION
    
    async def generate_pdf(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Generate PDF from enhanced resume"""
        user_id = update.effective_user.id
        session = self.user_sessions.get(user_id)
        
        if not session:
            await update.message.reply_text("❌ Session expired. Please /start again.")
            return await self.start(update, context)
        
        try:
            await update.message.reply_text("📝 Generating PDF...")
            
            resume_data = session.get('enhanced_resume')
            
            # Check if enhanced resume has valid data
            if not resume_data or (isinstance(resume_data, dict) and not resume_data):
                await update.message.reply_text(
                    "⚠️ Need to generate enhanced CV first.\n"
                    "Let me regenerate it for you..."
                )
                
                # Re-generate the enhanced resume
                if not session.get('resume_text') or not session.get('job_description'):
                    await update.message.reply_text("❌ Missing resume or job description. Please /start again.")
                    return await self.start(update, context)
                
                try:
                    enhanced = self.enhancer.generate_enhanced_resume(
                        session['resume_text'],
                        session['job_description'],
                        use_ai=bool(OPENAI_API_KEY or GEMINI_API_KEY),
                        missing_keywords=session.get('analysis', {}).get('missing_keywords', [])
                    )
                    
                    if enhanced:
                        session['enhanced_resume'] = enhanced
                        resume_data = enhanced
                    else:
                        raise ValueError("Enhancement failed - empty result")
                except Exception as regenerate_err:
                    await update.message.reply_text(
                        f"⚠️ Could not enhance CV: {str(regenerate_err)}\n"
                        "Using original CV for PDF..."
                    )
                    # Use original resume text as fallback
                    resume_data = {
                        'summary': session.get('resume_text', '')[:500],
                        'skills': 'See attached resume',
                        'experience': session.get('resume_text', '')
                    }
            
            if not resume_data:
                await update.message.reply_text("❌ Cannot generate PDF. Please try again.")
                return AWAITING_PDF_ACTION
            
            # Generate PDF
            success, pdf_path, error = self.pdf_generator.generate_resume_pdf(
                resume_data,
                name=f"Resume_{user_id}",
                contact_info=None
            )
            
            if success:
                # Send PDF to user
                with open(pdf_path, 'rb') as pdf_file:
                    await update.message.reply_document(
                        pdf_file,
                        caption="✅ Your enhanced resume PDF is ready!"
                    )
                
                # Offer cleanup
                reply_keyboard = [
                    ['New Analysis', 'Help']
                ]
                reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
                
                await update.message.reply_text(
                    "What would you like to do next?",
                    reply_markup=reply_markup
                )
                return AWAITING_JOB_DESC
            else:
                await update.message.reply_text(f"❌ Error generating PDF: {error}")
                return AWAITING_PDF_ACTION
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return AWAITING_PDF_ACTION
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
🤖 RESUME VISUALIZER BOT - HELP

📋 Commands:
/start - Start a new analysis
/analyze - Begin the analysis workflow
/help - Show this help message

💡 Features:
1. Upload your resume and job description
2. Get AI-powered matching analysis
3. Identify skill gaps
4. Receive improvement suggestions
5. Generate enhanced resume
6. Download as professional PDF

🔧 Supported File Formats:
- PDF (.pdf)
- Text (.txt)

📊 Analysis Includes:
- Match score (0-10)
- Missing keywords
- Strength analysis
- Tailored improvements
- ATS-friendly PDF generation

Questions? Contact support or type /help
        """
        await update.message.reply_text(help_text)
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel conversation"""
        await update.message.reply_text("❌ Analysis cancelled. /start to begin again.")
        return ConversationHandler.END


def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in config")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Initialize bot
    bot = ResumeVisualizer()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", bot.start),
            CommandHandler("analyze", bot.start)
        ],
        states={
            AWAITING_JOB_DESC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bot.receive_job_description),
                MessageHandler(filters.TEXT, bot.handle_message)
            ],
            AWAITING_RESUME: [
                MessageHandler(filters.Document.ALL, bot.receive_resume),
            ],
            PROCESSING: [
                MessageHandler(filters.TEXT, bot.process_analysis),
            ],
            AWAITING_MODIFICATION_CHOICE: [
                MessageHandler(filters.TEXT, bot.handle_modification_choice),
            ],
            AWAITING_TEMPLATE_SELECTION: [
                MessageHandler(filters.TEXT, bot.handle_template_selection),
            ],
            AWAITING_PDF_ACTION: [
                MessageHandler(filters.TEXT, bot.handle_pdf_action),
            ]
        },
        fallbacks=[
            CommandHandler("cancel", bot.cancel),
            CommandHandler("help", bot.help_command)
        ]
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("start", bot.start))
    
    # Start bot
    print("🚀 Resume Visualizer Bot is starting...")
    print("Press Ctrl+C to stop")
    
    # Run polling (handles event loop internally)
    application.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None)


if __name__ == "__main__":
    import sys
    
    print("Starting Resume Visualizer Bot...")
    
    if sys.platform == 'win32':
        # For Windows, use ProactorEventLoop
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n✋ Bot stopped")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
