# app/services/github_service.py
import os
import logging
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.config import settings
from app.models import User, Portfolio, SyncLog

logger = logging.getLogger(__name__)


class GitHubService:
    """GitHub API service for fetching repository and user data"""
    
    def __init__(self):
        self.api_url = settings.GITHUB_API_URL
        self.token = settings.GITHUB_TOKEN
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.client = httpx.Client(timeout=30.0)
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get GitHub user profile"""
        try:
            response = await self.client.get(
                f"{self.api_url}/users/{username}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "login": data.get("login"),
                "name": data.get("name"),
                "bio": data.get("bio"),
                "avatar_url": data.get("avatar_url"),
                "followers": data.get("followers"),
                "public_repos": data.get("public_repos"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at")
            }
        except httpx.HTTPError as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise
    
    async def get_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Get user repositories with details"""
        try:
            response = await self.client.get(
                f"{self.api_url}/users/{username}/repos",
                headers=self.headers,
                params={"sort": "updated", "per_page": 50}
            )
            response.raise_for_status()
            repos = response.json()
            
            projects = []
            for repo in repos:
                # Get languages
                lang_response = await self.client.get(
                    f"{self.api_url}/repos/{username}/{repo['name']}/languages",
                    headers=self.headers
                )
                languages = lang_response.json() if lang_response.status_code == 200 else {}
                
                projects.append({
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "stars": repo.get("stargazers_count", 0),
                    "tech_stack": list(languages.keys()),
                    "url": repo.get("html_url"),
                    "updated_at": repo.get("updated_at"),
                    "fork": repo.get("fork", False)
                })
            
            return projects
        except httpx.HTTPError as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitHub webhook payload"""
        event_type = payload.get("action", "unknown")
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        
        return {
            "event_type": event_type,
            "repository": repository.get("name"),
            "full_name": repository.get("full_name"),
            "sender": sender.get("login"),
            "timestamp": datetime.utcnow().isoformat()
        }