# app/agents/portfolio_agent.py
import os
import json
import logging
from typing import Dict, List, Any, Optional
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

from app.config import settings
from app.schemas import PortfolioStateSchema
from app.utils.validators import validate_portfolio_state

logger = logging.getLogger(__name__)


class PortfolioAgent:
    """Agent for processing and structuring portfolio data"""
    
    def __init__(self):
        self.model = settings.OPENROUTER_MODEL
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        
        # Initialize LLM with OpenRouter
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0.3,
            timeout=settings.OPENROUTER_TIMEOUT
        )
    
    def create_aggregator_agent(self) -> Agent:
        """Create agent for aggregating data"""
        return Agent(
            role="Portfolio Data Aggregator",
            goal="Aggregate and structure portfolio data from multiple sources",
            backstory="""You are an expert at combining data from GitHub, LinkedIn, 
            and resume sources into a unified portfolio structure. You ensure data 
            consistency and quality.""",
            allow_delegation=False,
            verbose=True,
            llm=self.llm
        )
    
    def create_sanitizer_agent(self) -> Agent:
        """Create agent for sanitizing data"""
        return Agent(
            role="Data Sanitization Specialist",
            goal="Clean and validate portfolio data",
            backstory="""You are a data quality expert who ensures all portfolio 
            data meets strict quality standards. You remove duplicates, fix formatting, 
            and validate all entries.""",
            allow_delegation=False,
            verbose=True,
            llm=self.llm
        )
    
    async def process_raw_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw data using agents"""
        try:
            aggregator = self.create_aggregator_agent()
            sanitizer = self.create_sanitizer_agent()
            
            # Create tasks
            aggregate_task = Task(
                description=f"""
                Aggregate the following raw data into a structured portfolio:
                
                Raw Data:
                {json.dumps(raw_data, indent=2)}
                
                Required structure:
                {{
                    "profile": {{"name": "", "headline": "", "avatar_url": ""}},
                    "experience": [{{"company": "", "role": "", "duration": "", "bullets": []}}],
                    "projects": [{{"name": "", "description": "", "stars": 0, "tech_stack": [], "url": ""}}],
                    "education": [{{"institution": "", "degree": "", "field_of_study": ""}}],
                    "certifications": [{{"name": "", "issuer": "", "issue_date": ""}}],
                    "skills": []
                }}
                """,
                expected_output="A structured portfolio JSON object",
                agent=aggregator
            )
            
            sanitize_task = Task(
                description=f"""
                Sanitize and validate the following portfolio data:
                
                Data: {{aggregated_data}}
                
                Ensure:
                1. All strings are properly trimmed
                2. No duplicates in lists
                3. Required fields are present
                4. Data types are correct
                5. Remove any invalid entries
                """,
                expected_output="A clean, validated portfolio JSON object",
                agent=sanitizer
            )
            
            # Create crew
            crew = Crew(
                agents=[aggregator, sanitizer],
                tasks=[aggregate_task, sanitize_task],
                verbose=True
            )
            
            # Execute
            result = crew.kickoff(inputs={"raw_data": raw_data})
            
            # Parse and validate result
            processed = self._parse_result(str(result))
            
            # Validate against schema
            validated = validate_portfolio_state(processed)
            
            return validated
            
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            return self._get_default_portfolio()
    
    def _parse_result(self, result: str) -> Dict[str, Any]:
        """Parse agent result with strict JSON validation"""
        try:
            # Try to extract JSON from the result
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data
            
            # Fallback: try direct parse
            return json.loads(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return self._get_default_portfolio()
    
    def _get_default_portfolio(self) -> Dict[str, Any]:
        """Get default portfolio data"""
        return {
            "profile": {
                "name": "Your Name",
                "headline": "Software Engineer",
                "avatar_url": ""
            },
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
            "skills": []
        }