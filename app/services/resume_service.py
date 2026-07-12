# app/services/resume_service.py
import os
import json
import logging
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
import PyPDF2
import pdfplumber

from app.config import settings

logger = logging.getLogger(__name__)


class ResumeService:
    """Resume parsing and storage service"""
    
    def __init__(self):
        self.storage_url = settings.RESUME_STORAGE_URL
        self.json_url = settings.RESUME_JSON_URL
        self.client = httpx.Client(timeout=30.0)
    
    async def get_resume_data(self) -> Dict[str, Any]:
        """Get resume data from JSON or parse PDF"""
        try:
            # Try JSON first
            if self.json_url:
                response = await self.client.get(self.json_url)
                if response.status_code == 200:
                    return response.json()
            
            # If no JSON, try to parse from storage
            if self.storage_url:
                return await self._parse_pdf_from_storage()
            
            return await self._get_default_resume()
            
        except Exception as e:
            logger.error(f"Resume fetch failed: {str(e)}")
            return await self._get_default_resume()
    
    async def _parse_pdf_from_storage(self) -> Dict[str, Any]:
        """Parse PDF resume from storage"""
        try:
            # Assuming S3 or similar storage
            response = await self.client.get(self.storage_url)
            if response.status_code != 200:
                return await self._get_default_resume()
            
            # Parse PDF
            with pdfplumber.open(response.content) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
                
                return self._parse_resume_text(text)
                
        except Exception as e:
            logger.error(f"PDF parsing failed: {str(e)}")
            return await self._get_default_resume()
    
    def _parse_resume_text(self, text: str) -> Dict[str, Any]:
        """Parse resume text into structured data"""
        lines = text.split('\n')
        
        resume_data = {
            "name": "",
            "headline": "",
            "experience": [],
            "education": [],
            "skills": [],
            "certifications": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "EXPERIENCE" in line.upper() or "WORK" in line.upper():
                current_section = "experience"
                continue
            elif "EDUCATION" in line.upper():
                current_section = "education"
                continue
            elif "SKILLS" in line.upper():
                current_section = "skills"
                continue
            elif "CERTIFICATION" in line.upper():
                current_section = "certifications"
                continue
            
            # Parse content
            if current_section == "experience":
                resume_data["experience"].append({
                    "company": line[:50],
                    "role": line[50:100] if len(line) > 50 else "",
                    "duration": "",
                    "bullets": []
                })
            elif current_section == "skills":
                if "," in line:
                    resume_data["skills"].extend([s.strip() for s in line.split(",")])
                else:
                    resume_data["skills"].append(line)
            elif current_section == "education":
                resume_data["education"].append({
                    "institution": line,
                    "degree": "",
                    "field_of_study": ""
                })
        
        return resume_data
    
    async def _get_default_resume(self) -> Dict[str, Any]:
        """Get default resume data"""
        return {
            "name": "Your Name",
            "headline": "Software Engineer | Full Stack Developer",
            "experience": [
                {
                    "company": "Example Company",
                    "role": "Senior Developer",
                    "duration": "2020 - Present",
                    "bullets": ["Built scalable applications", "Led team of 5 developers"]
                }
            ],
            "education": [
                {
                    "institution": "University Name",
                    "degree": "B.S. Computer Science",
                    "field_of_study": "Computer Science"
                }
            ],
            "skills": ["Python", "JavaScript", "React", "Node.js"],
            "certifications": []
        }