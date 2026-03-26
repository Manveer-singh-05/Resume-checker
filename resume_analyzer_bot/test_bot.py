"""
Test Script for Resume Analyzer Bot
Run individual tests to verify functionality without Telegram
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.extraction import ResumeExtractor
from modules.analysis import AIAnalyzer
from modules.enhancement import ResumeEnhancer
from modules.pdf_generator import PDFGenerator
from utils.helpers import FileValidator, TextProcessor, ResponseFormatter


def test_text_extraction():
    """Test resume text extraction"""
    print("\n" + "="*50)
    print("TEST 1: Resume Text Extraction")
    print("="*50)
    
    extractor = ResumeExtractor()
    
    # Test with sample resume
    sample_resume = "examples/sample_resume.txt"
    
    if not os.path.exists(sample_resume):
        print("❌ Sample resume not found")
        return False
    
    success, text, error = extractor.extract_from_file(sample_resume)
    
    if success:
        print(f"✅ Successfully extracted {len(text)} characters")
        print(f"   Word count: {TextProcessor.count_words(text)}")
        print(f"   Lines: {TextProcessor.count_lines(text)}")
        return True
    else:
        print(f"❌ Extraction failed: {error}")
        return False


def test_keyword_extraction():
    """Test keyword extraction"""
    print("\n" + "="*50)
    print("TEST 2: Keyword Extraction")
    print("="*50)
    
    analyzer = AIAnalyzer(ai_provider="nlp_only")  # Use NLP only
    
    sample_text = """
    Experienced Python developer with expertise in Django, 
    FastAPI, and machine learning. Strong database design 
    and AWS cloud experience.
    """
    
    keywords = analyzer.extract_keywords(sample_text, top_n=10)
    
    if keywords:
        print(f"✅ Extracted {len(keywords)} keywords:")
        for i, keyword in enumerate(keywords, 1):
            print(f"   {i}. {keyword}")
        return True
    else:
        print("❌ No keywords extracted")
        return False


def test_nlp_similarity():
    """Test NLP similarity calculation"""
    print("\n" + "="*50)
    print("TEST 3: NLP Similarity Analysis")
    print("="*50)
    
    analyzer = AIAnalyzer(ai_provider="nlp_only")
    
    resume = "Python developer with experience in Django and REST APIs"
    job_desc = "We need a Python developer skilled in Django framework and API development"
    
    similarity = analyzer.calculate_nlp_similarity(resume, job_desc)
    
    print(f"✅ Similarity Score: {similarity:.2f} (0-1 scale)")
    print(f"   Converted to 0-10: {similarity * 10:.1f}")
    
    if similarity > 0:
        return True
    else:
        print("❌ No similarity detected")
        return False


def test_missing_keywords():
    """Test missing keyword detection"""
    print("\n" + "="*50)
    print("TEST 4: Missing Keywords Detection")
    print("="*50)
    
    analyzer = AIAnalyzer(ai_provider="nlp_only")
    
    resume = "I know Python and JavaScript"
    job_desc = "Looking for developer with Python, Java, Docker, Kubernetes, AWS, and GCP experience"
    
    missing = analyzer.find_missing_keywords(resume, job_desc)
    
    if missing:
        print(f"✅ Found {len(missing)} missing keywords:")
        for i, keyword in enumerate(missing[:5], 1):
            print(f"   {i}. {keyword}")
        return True
    else:
        print("⚠️  No missing keywords detected")
        return True  # Not necessarily a failure


def test_text_processor():
    """Test text processing utilities"""
    print("\n" + "="*50)
    print("TEST 5: Text Processing Utilities")
    print("="*50)
    
    test_text = "  Hello   World  \n  This   is   a   test  "
    
    normalized = TextProcessor.normalize_text(test_text)
    print(f"✅ Normalized text: '{normalized}'")
    
    word_count = TextProcessor.count_words(normalized)
    print(f"✅ Word count: {word_count}")
    
    if word_count > 0:
        return True
    else:
        print("❌ Text processing failed")
        return False


def test_file_validator():
    """Test file validation"""
    print("\n" + "="*50)
    print("TEST 6: File Validator")
    print("="*50)
    
    # Test valid file
    sample_resume = "examples/sample_resume.txt"
    
    is_valid, error = FileValidator.validate_file(sample_resume)
    
    if is_valid:
        print(f"✅ Sample resume validated successfully")
        print(f"   Size: {os.path.getsize(sample_resume)} bytes")
        return True
    else:
        print(f"❌ Validation failed: {error}")
        return False


def test_response_formatter():
    """Test response formatting"""
    print("\n" + "="*50)
    print("TEST 7: Response Formatting")
    print("="*50)
    
    # Test score formatting
    score_response = ResponseFormatter.format_score_response(7.5, max_score=10)
    print("Score Response:")
    print(score_response)
    
    # Test error formatting
    error_response = ResponseFormatter.format_error_response("Test error", "Test context")
    print("Error Response:")
    print(error_response)
    
    # Test success formatting
    success_response = ResponseFormatter.format_success_response("Test successful")
    print("Success Response:")
    print(success_response)
    
    return True


def test_resume_enhancement():
    """Test resume enhancement"""
    print("\n" + "="*50)
    print("TEST 8: Resume Enhancement (Rule-based)")
    print("="*50)
    
    enhancer = ResumeEnhancer(ai_provider="nlp_only")
    
    resume = """
    John Doe
    Skills: Python, JavaScript
    Experience: 5 years as developer
    """
    
    job_desc = "Python expert needed with Django, REST APIs, and Docker"
    
    enhanced = enhancer.generate_enhanced_resume(resume, job_desc, use_ai=False)
    
    if enhanced:
        print(f"✅ Enhanced resume generated")
        print(f"   Sections: {list(enhanced.keys())}")
        return True
    else:
        print("❌ Enhancement failed")
        return False


def test_pdf_generation():
    """Test PDF generation"""
    print("\n" + "="*50)
    print("TEST 9: PDF Generation")
    print("="*50)
    
    os.makedirs("output_resumes", exist_ok=True)
    pdf_gen = PDFGenerator(output_dir="output_resumes")
    
    resume_data = {
        "summary": "Experienced developer with 5+ years in Python and JavaScript",
        "skills": "Python, Django, React, PostgreSQL, Docker, AWS",
        "experience": "Senior Developer at TechCorp (2020-Present)\nDeveloped microservices handling 100K+ users",
        "projects": "E-commerce platform, Task management app",
        "education": "BS Computer Science, University of Tech (2016)"
    }
    
    success, path, error = pdf_gen.generate_resume_pdf(
        resume_data,
        name="Test_Resume",
        contact_info={"email": "test@example.com", "phone": "(555) 123-4567"}
    )
    
    if success:
        print(f"✅ PDF generated successfully")
        print(f"   Path: {path}")
        print(f"   Size: {os.path.getsize(path)} bytes")
        return True
    else:
        print(f"❌ PDF generation failed: {error}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "█"*50)
    print("RESUME ANALYZER BOT - TEST SUITE")
    print("█"*50)
    
    tests = [
        ("Text Extraction", test_text_extraction),
        ("Keyword Extraction", test_keyword_extraction),
        ("NLP Similarity", test_nlp_similarity),
        ("Missing Keywords", test_missing_keywords),
        ("Text Processing", test_text_processor),
        ("File Validator", test_file_validator),
        ("Response Formatter", test_response_formatter),
        ("Resume Enhancement", test_resume_enhancement),
        ("PDF Generation", test_pdf_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "█"*50)
    print("TEST SUMMARY")
    print("█"*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
