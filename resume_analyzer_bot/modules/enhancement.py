"""
Resume Enhancement Module
Generates improved resume versions tailored to job descriptions
"""

import json
from typing import Dict, List, Optional

try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class ResumeEnhancer:
    """Generate and enhance resume content using AI"""
    
    def __init__(self, ai_provider: str = "openai", api_key: str = None, model: str = None):
        """
        Initialize Resume Enhancer
        
        Args:
            ai_provider: 'openai' or 'gemini'
            api_key: API key for the chosen provider
            model: Model name
        """
        self.ai_provider = ai_provider
        self.api_key = api_key
        self.model = model or "gpt-3.5-turbo"
        
        if ai_provider == "openai" and api_key:
            openai.api_key = api_key
        elif ai_provider == "gemini" and api_key:
            genai.configure(api_key=api_key)
    
    def generate_enhanced_resume(
        self, 
        resume_text: str, 
        job_desc: str,
        use_ai: bool = True,
        missing_keywords: List[str] = None
    ) -> Dict[str, str]:
        """
        Generate enhanced resume tailored to job description
        
        Args:
            resume_text: Original resume content
            job_desc: Target job description
            use_ai: Whether to use AI for enhancement
            missing_keywords: List of identified missing keywords to target
            
        Returns:
            Dictionary with resume sections
        """
        if missing_keywords is None:
            missing_keywords = []
        if use_ai and self.api_key:
            return self._enhance_with_ai(resume_text, job_desc, missing_keywords)
        else:
            return self._enhance_with_rules(resume_text, job_desc, missing_keywords)
    
    def _enhance_with_ai(self, resume_text: str, job_desc: str, missing_keywords: List[str] = None) -> Dict[str, str]:
        """Enhance resume using AI"""
        if missing_keywords is None:
            missing_keywords = []
        try:
            if self.ai_provider == "openai":
                return self._enhance_openai(resume_text, job_desc, missing_keywords)
            elif self.ai_provider == "gemini":
                return self._enhance_gemini(resume_text, job_desc, missing_keywords)
        except Exception as e:
            print(f"AI enhancement error: {e}")
            return self._enhance_with_rules(resume_text, job_desc, missing_keywords)
    
    def _enhance_openai(self, resume_text: str, job_desc: str, missing_keywords: List[str] = None) -> Dict[str, str]:
        """Enhance using OpenAI"""
        if missing_keywords is None:
            missing_keywords = []
        try:
            keywords_text = ""
            if missing_keywords:
                keywords_text = f"\n\nIMPORTANT - The following skills/keywords were identified as MISSING from the original resume and MUST be incorporated:\n- {chr(10).join(f'- {kw}' for kw in missing_keywords)}\n\nMake sure these keywords are naturally integrated into the appropriate sections."
            
            prompt = f"""Based on the job description, enhance and tailor the following resume. 
For each section, incorporate relevant keywords from the job description while maintaining authenticity.{keywords_text}

Resume:
{resume_text}

Job Description:
{job_desc}

Generate an improved resume with these sections (respond in JSON format):
{{
  "summary": "Professional summary tailored to the job, incorporating relevant keywords",
  "skills": "Comma-separated relevant skills including the missing keywords above",
  "experience": "Enhanced experience section with job description keywords and the identified missing skills",
  "projects": "Relevant projects if applicable",
  "education": "Education section"
}}"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return {
                "summary": result.get("summary", ""),
                "skills": result.get("skills", ""),
                "experience": result.get("experience", ""),
                "projects": result.get("projects", ""),
                "education": result.get("education", "")
            }
        except Exception as e:
            print(f"OpenAI enhancement error: {e}")
            return {}
    
    def _enhance_gemini(self, resume_text: str, job_desc: str, missing_keywords: List[str] = None) -> Dict[str, str]:
        """Enhance using Google Gemini"""
        if missing_keywords is None:
            missing_keywords = []
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            keywords_text = ""
            if missing_keywords:
                keywords_text = f"\n\nIMPORTANT - The following skills/keywords were identified as MISSING from the original resume and MUST be incorporated:\n- {chr(10).join(f'- {kw}' for kw in missing_keywords)}\n\nMake sure these keywords are naturally integrated into the appropriate sections."
            
            prompt = f"""Based on the job description, enhance and tailor the following resume. 
For each section, incorporate relevant keywords from the job description while maintaining authenticity.{keywords_text}

Resume:
{resume_text}

Job Description:
{job_desc}

Generate an improved resume with these sections (respond in JSON format):
{{
  "summary": "Professional summary tailored to the job, incorporating relevant keywords",
  "skills": "Comma-separated relevant skills including the missing keywords above",
  "experience": "Enhanced experience section with job description keywords and the identified missing skills",
  "projects": "Relevant projects if applicable",
  "education": "Education section"
}}"""
            
            response = model.generate_content(prompt)
            result_text = response.text
            result = json.loads(result_text)
            
            return {
                "summary": result.get("summary", ""),
                "skills": result.get("skills", ""),
                "experience": result.get("experience", ""),
                "projects": result.get("projects", ""),
                "education": result.get("education", "")
            }
        except Exception as e:
            print(f"Gemini enhancement error: {e}")
            return {}
    
    def _enhance_with_rules(self, resume_text: str, job_desc: str, missing_keywords: List[str] = None) -> Dict[str, str]:
        """Enhance using rule-based approach"""
        if missing_keywords is None:
            missing_keywords = []
        try:
            sections = self._parse_resume_sections(resume_text)
            job_keywords = self._extract_job_keywords(job_desc)
            
            # Add missing keywords to the keywords to incorporate
            all_keywords = list(set(job_keywords + missing_keywords))
            
            # Enhance each section
            enhanced = {
                "summary": self._enhance_summary(sections.get("summary", ""), all_keywords),
                "skills": self._enhance_skills(sections.get("skills", ""), all_keywords),
                "experience": self._enhance_experience(sections.get("experience", ""), all_keywords),
                "projects": sections.get("projects", ""),
                "education": sections.get("education", "")
            }
            
            return enhanced
        except Exception as e:
            print(f"Rule-based enhancement error: {e}")
            return {}
    
    def _parse_resume_sections(self, text: str) -> Dict[str, str]:
        """Parse resume into standard sections"""
        sections = {
            "summary": "",
            "skills": "",
            "experience": "",
            "projects": "",
            "education": ""
        }
        
        # Simple parsing based on common section headers
        lines = text.split('\n')
        current_section = "summary"
        summary_lines = []
        
        for line in lines:
            line_lower = line.lower()
            
            if any(keyword in line_lower for keyword in ['skill', 'competenc']):
                current_section = "skills"
            elif any(keyword in line_lower for keyword in ['experience', 'work', 'employment']):
                current_section = "experience"
            elif any(keyword in line_lower for keyword in ['project', 'portfolio']):
                current_section = "projects"
            elif any(keyword in line_lower for keyword in ['education', 'degree', 'university']):
                current_section = "education"
            else:
                if current_section == "summary" and len(summary_lines) < 5:
                    summary_lines.append(line)
                else:
                    sections[current_section] += line + "\n"
        
        sections["summary"] = "\n".join(summary_lines)
        return sections
    
    def _extract_job_keywords(self, job_desc: str) -> List[str]:
        """Extract important keywords from job description"""
        keywords = []
        for word in job_desc.split():
            word = word.strip('.,;:!?').lower()
            if len(word) > 4 and word not in ['that', 'this', 'with', 'from', 'have', 'will']:
                keywords.append(word)
        return list(set(keywords))[:30]
    
    def _enhance_summary(self, summary: str, keywords: List[str]) -> str:
        """Enhance professional summary with job keywords"""
        if not summary:
            keywords_str = ", ".join(keywords[:5])
            return f"Results-driven professional with expertise in {keywords_str}."
        
        # Add relevant keywords to summary
        enhanced = summary + f"\n\nKey competencies: {', '.join(keywords[:8])}"
        return enhanced
    
    def _enhance_skills(self, skills: str, keywords: List[str]) -> str:
        """Enhance skills section by adding job-relevant keywords"""
        if not skills:
            return ", ".join(keywords[:15])
        
        # Combine existing skills with relevant keywords
        skill_list = [s.strip() for s in skills.split(',')]
        skill_list.extend(keywords[:10])
        skill_list = list(set(skill_list))
        return ", ".join(skill_list)
    
    def _enhance_experience(self, experience: str, keywords: List[str]) -> str:
        """Enhance experience section with relevant keywords"""
        if not experience:
            return "Professional experience incorporating key industry skills."
        
        # Add keywords to experience section strategically
        enhanced = experience
        for keyword in keywords[:5]:
            if keyword not in enhanced.lower():
                enhanced += f"\n• Demonstrated proficiency in {keyword}"
        
        return enhanced
