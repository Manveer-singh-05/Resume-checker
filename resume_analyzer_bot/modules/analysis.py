"""
AI Analysis Module
Performs NLP-based analysis and AI-powered resume scoring
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class AIAnalyzer:
    """Analyze resume vs job description using AI and NLP"""
    
    def __init__(self, ai_provider: str = "openai", api_key: str = None, model: str = None):
        """
        Initialize AI Analyzer
        
        Args:
            ai_provider: 'openai' or 'gemini'
            api_key: API key for the chosen provider
            model: Model name (e.g., 'gpt-3.5-turbo')
        """
        self.ai_provider = ai_provider
        self.api_key = api_key
        self.model = model or "gpt-3.5-turbo"
        
        if ai_provider == "openai" and api_key:
            openai.api_key = api_key
        elif ai_provider == "gemini" and api_key:
            genai.configure(api_key=api_key)
        
        # Download NLTK data if needed
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """
        Extract keywords from text using TF-IDF
        
        Args:
            text: Input text
            top_n: Number of top keywords to extract
            
        Returns:
            List of keywords
        """
        try:
            vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english')
            vectorizer.fit([text])
            keywords = vectorizer.get_feature_names_out().tolist()
            return keywords
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def calculate_nlp_similarity(self, resume_text: str, job_desc: str) -> float:
        """
        Calculate similarity between resume and job description using TF-IDF
        
        Args:
            resume_text: Resume content
            job_desc: Job description content
            
        Returns:
            Similarity score (0-1)
        """
        try:
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([resume_text, job_desc])
            similarity = cosine_similarity(vectors)[0][1]
            return float(similarity)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def find_missing_keywords(self, resume_text: str, job_desc: str) -> List[str]:
        """
        Find keywords in job description not present in resume
        
        Args:
            resume_text: Resume content
            job_desc: Job description content
            
        Returns:
            List of missing keywords
        """
        try:
            # Extract keywords from both
            job_keywords = set(self.extract_keywords(job_desc, top_n=30))
            resume_text_lower = resume_text.lower()
            
            # Find keywords not in resume
            missing = []
            for keyword in job_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in resume_text_lower:
                    missing.append(keyword)
            
            return missing[:15]  # Return top 15 missing
        except Exception as e:
            print(f"Error finding missing keywords: {e}")
            return []
    
    def analyze_with_ai(self, resume_text: str, job_desc: str) -> Tuple[float, str, str]:
        """
        Use AI to analyze resume vs job description with smart fallback
        
        Args:
            resume_text: Resume content
            job_desc: Job description content
            
        Returns:
            Tuple of (score, analysis, suggestions)
        """
        try:
            # Try primary provider
            if self.ai_provider == "openai":
                score, analysis, suggestions = self._analyze_with_openai(resume_text, job_desc)
                # If OpenAI fails with quota error, try Gemini
                if "insufficient_quota" in suggestions.lower() or "API Error" in suggestions:
                    print("OpenAI quota exceeded, trying Gemini...")
                    score, analysis, suggestions = self._analyze_with_gemini(resume_text, job_desc)
                # If Gemini also fails, use NLP
                if "API Error" in suggestions or "error" in suggestions.lower():
                    print("AI providers failed, using NLP fallback...")
                    score, analysis, suggestions = self._analyze_with_nlp(resume_text, job_desc)
                return score, analysis, suggestions
            elif self.ai_provider == "gemini":
                score, analysis, suggestions = self._analyze_with_gemini(resume_text, job_desc)
                # If Gemini fails, try OpenAI
                if "API Error" in suggestions or "error" in suggestions.lower():
                    print("Gemini failed, trying OpenAI...")
                    score, analysis, suggestions = self._analyze_with_openai(resume_text, job_desc)
                # If OpenAI also fails with quota, use NLP
                if "insufficient_quota" in suggestions.lower() or "API Error" in suggestions:
                    print("AI providers failed, using NLP fallback...")
                    score, analysis, suggestions = self._analyze_with_nlp(resume_text, job_desc)
                return score, analysis, suggestions
            else:
                return self._analyze_with_nlp(resume_text, job_desc)
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            # Last resort: use NLP
            return self._analyze_with_nlp(resume_text, job_desc)
    
    def _analyze_with_openai(self, resume_text: str, job_desc: str) -> Tuple[float, str, str]:
        """Analyze using OpenAI API"""
        try:
            from openai import OpenAI, APIError, APIConnectionError, APITimeoutError, RateLimitError
            
            client = OpenAI(api_key=self.api_key)
            
            prompt = f"""Analyze the following resume against the job description and provide:
1. A matching score from 0-10
2. Key strengths
3. Missing skills or experience
4. Specific improvement suggestions

Resume:
{resume_text[:2000]}

Job Description:
{job_desc[:2000]}

Respond with ONLY a valid JSON object (no markdown, no code blocks) with keys: score, strengths, missing_items, suggestions"""
            
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert resume analyzer. Respond with valid JSON only, no markdown."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    timeout=30  # 30 second timeout
                )
                
                result_text = response.choices[0].message.content
                
                # Parse JSON response
                try:
                    # Clean up markdown formatting if present
                    if "```json" in result_text:
                        result_text = result_text.split("```json")[1].split("```")[0]
                    elif "```" in result_text:
                        result_text = result_text.split("```")[1].split("```")[0]
                    
                    result = json.loads(result_text)
                    score = float(result.get('score', 0))
                    analysis = result.get('strengths', '')
                    suggestions = result.get('suggestions', '')
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {result_text}")
                    return 6.5, "Analysis completed", "Please review recommendations"
                
                return score, analysis, suggestions
            except RateLimitError as rate_err:
                print(f"OpenAI rate limit: {rate_err}")
                return 0.0, "", "API Error: insufficient_quota"
            except (APITimeoutError, APIConnectionError) as timeout_err:
                print(f"API timeout/connection error: {timeout_err}")
                return 0.0, "", "API timeout - using NLP fallback"
            except APIError as api_err:
                error_msg = str(api_err)
                print(f"OpenAI API error: {api_err}")
                if "insufficient_quota" in error_msg.lower() or "429" in error_msg:
                    return 0.0, "", "API Error: insufficient_quota"
                return 0.0, "", f"API Error: {str(api_err)}"
                
        except Exception as e:
            print(f"OpenAI error: {e}")
            error_msg = str(e)
            if "insufficient_quota" in error_msg.lower() or "429" in error_msg:
                return 0.0, "", "API Error: insufficient_quota"
            print("Falling back to NLP analysis...")
            return self._analyze_with_nlp(resume_text, job_desc)
    
    def _analyze_with_gemini(self, resume_text: str, job_desc: str) -> Tuple[float, str, str]:
        """Analyze using Google Gemini API"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""Analyze the following resume against the job description and provide:
1. A matching score from 0-10
2. Key strengths
3. Missing skills or experience
4. Specific improvement suggestions

Resume:
{resume_text[:2000]}

Job Description:
{job_desc[:2000]}

Respond with ONLY a valid JSON object with keys: score, strengths, missing_items, suggestions"""
            
            try:
                response = model.generate_content(prompt, timeout=30)
                result_text = response.text
                
                # Parse JSON response
                try:
                    # Clean up markdown if present
                    if "```json" in result_text:
                        result_text = result_text.split("```json")[1].split("```")[0]
                    elif "```" in result_text:
                        result_text = result_text.split("```")[1].split("```")[0]
                    
                    result = json.loads(result_text)
                    score = float(result.get('score', 0))
                    analysis = result.get('strengths', '')
                    suggestions = result.get('suggestions', '')
                except json.JSONDecodeError:
                    print(f"Failed to parse Gemini JSON: {result_text}")
                    return 6.5, "Analysis completed", "Please review recommendations"
                
                return score, analysis, suggestions
            except Exception as api_err:
                error_msg = str(api_err)
                print(f"Gemini API error: {api_err}")
                if "quota" in error_msg.lower() or "resource" in error_msg.lower():
                    return 0.0, "", "API Error: insufficient_quota"
                return 0.0, "", f"API Error: {error_msg}"
                
        except Exception as e:
            print(f"Gemini error: {e}")
            error_msg = str(e)
            if "quota" in error_msg.lower():
                return 0.0, "", "API Error: insufficient_quota"
            return 0.0, "", str(e)
    
    def _analyze_with_nlp(self, resume_text: str, job_desc: str) -> Tuple[float, str, str]:
        """Analyze using only NLP (no AI API needed)"""
        try:
            # Calculate similarity
            similarity = self.calculate_nlp_similarity(resume_text, job_desc)
            score = min(10, similarity * 12)  # Convert to 0-10 scale
            
            # Find missing keywords
            missing = self.find_missing_keywords(resume_text, job_desc)
            
            # Extract job keywords
            job_keywords = self.extract_keywords(job_desc, top_n=10)
            
            analysis = f"Resume contains {len(set(word for word in resume_text.split()))} unique words. "
            analysis += f"Job description contains {len(job_keywords)} key terms."
            
            missing_str = ", ".join(missing[:10]) if missing else "No major gaps identified"
            suggestions = f"Consider adding: {missing_str}"
            
            return score, analysis, suggestions
        except Exception as e:
            print(f"NLP analysis error: {e}")
            return 0.0, "", str(e)
