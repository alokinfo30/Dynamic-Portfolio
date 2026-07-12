# app/services/linkedin_service.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re

from playwright.async_api import async_playwright, Browser, Page

from app.config import settings

logger = logging.getLogger(__name__)


class LinkedInService:
    """LinkedIn service for scraping profile data"""
    
    def __init__(self):
        self.email = settings.LINKEDIN_EMAIL
        self.password = settings.LINKEDIN_PASSWORD
        self.profile_url = settings.LINKEDIN_PROFILE_URL
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def initialize(self):
        """Initialize browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        await self._login()
    
    async def _login(self):
        """Login to LinkedIn"""
        try:
            await self.page.goto("https://www.linkedin.com/login")
            await self.page.fill("#username", self.email)
            await self.page.fill("#password", self.password)
            await self.page.click("button[type='submit']")
            await self.page.wait_for_load_state("networkidle")
            logger.info("LinkedIn login successful")
        except Exception as e:
            logger.error(f"LinkedIn login failed: {str(e)}")
            raise
    
    async def get_profile_data(self) -> Dict[str, Any]:
        """Scrape LinkedIn profile data"""
        try:
            await self.page.goto(self.profile_url)
            await self.page.wait_for_load_state("networkidle")
            
            # Extract profile data
            profile = {}
            
            # Name
            name_elem = await self.page.query_selector(".pv-top-card-section__name")
            if name_elem:
                profile["name"] = await name_elem.text_content()
            
            # Headline
            headline_elem = await self.page.query_selector(".pv-top-card-section__headline")
            if headline_elem:
                profile["headline"] = await headline_elem.text_content()
            
            # Experience
            profile["experience"] = await self._extract_experience()
            
            # Education
            profile["education"] = await self._extract_education()
            
            # Skills
            profile["skills"] = await self._extract_skills()
            
            # Certifications
            profile["certifications"] = await self._extract_certifications()
            
            return profile
            
        except Exception as e:
            logger.error(f"LinkedIn scraping failed: {str(e)}")
            raise
    
    async def _extract_experience(self) -> List[Dict[str, Any]]:
        """Extract experience section"""
        experiences = []
        try:
            # Click on experience section if needed
            exp_section = await self.page.query_selector("#experience-section")
            if exp_section:
                await exp_section.click()
                await self.page.wait_for_timeout(1000)
            
            # Extract experience items
            items = await self.page.query_selector_all(".experience-item")
            for item in items[:5]:  # Limit to 5 most recent
                company = await item.query_selector(".experience-company")
                role = await item.query_selector(".experience-title")
                duration = await item.query_selector(".experience-duration")
                
                exp = {
                    "company": await company.text_content() if company else "",
                    "role": await role.text_content() if role else "",
                    "duration": await duration.text_content() if duration else "",
                    "bullets": []
                }
                
                # Get description bullets
                bullets = await item.query_selector_all(".experience-description li")
                for bullet in bullets[:3]:
                    text = await bullet.text_content()
                    if text:
                        exp["bullets"].append(text.strip())
                
                experiences.append(exp)
        except Exception as e:
            logger.warning(f"Experience extraction failed: {str(e)}")
        
        return experiences
    
    async def _extract_education(self) -> List[Dict[str, Any]]:
        """Extract education section"""
        education = []
        try:
            items = await self.page.query_selector_all(".education-item")
            for item in items[:3]:
                school = await item.query_selector(".education-school")
                degree = await item.query_selector(".education-degree")
                
                edu = {
                    "institution": await school.text_content() if school else "",
                    "degree": await degree.text_content() if degree else "",
                    "field_of_study": "",
                    "start_date": "",
                    "end_date": ""
                }
                education.append(edu)
        except Exception as e:
            logger.warning(f"Education extraction failed: {str(e)}")
        
        return education
    
    async def _extract_skills(self) -> List[str]:
        """Extract skills section"""
        skills = []
        try:
            # Click on skills section
            skills_section = await self.page.query_selector("#skills-section")
            if skills_section:
                await skills_section.click()
                await self.page.wait_for_timeout(1000)
            
            items = await self.page.query_selector_all(".skill-item")
            for item in items[:20]:
                text = await item.text_content()
                if text:
                    skills.append(text.strip())
        except Exception as e:
            logger.warning(f"Skills extraction failed: {str(e)}")
        
        return skills
    
    async def _extract_certifications(self) -> List[Dict[str, Any]]:
        """Extract certifications"""
        certifications = []
        try:
            items = await self.page.query_selector_all(".certification-item")
            for item in items[:5]:
                name = await item.query_selector(".certification-name")
                issuer = await item.query_selector(".certification-issuer")
                
                cert = {
                    "name": await name.text_content() if name else "",
                    "issuer": await issuer.text_content() if issuer else "",
                    "issue_date": "",
                    "expiration_date": ""
                }
                certifications.append(cert)
        except Exception as e:
            logger.warning(f"Certification extraction failed: {str(e)}")
        
        return certifications
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()