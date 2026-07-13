# app/services/sync_service.py
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from app.worker import celery_app
from app.services.github_service import GitHubService
from app.services.linkedin_service import LinkedInService
from app.agents.portfolio_agent import PortfolioAgent
from app.database import get_db_session
from app.models import Portfolio, SyncLog

logger = logging.getLogger(__name__)


async def run_sync_flow(user_id: str) -> Dict[str, Any]:
    """
    Asynchronously runs the full data sync and processing flow.
    This function is designed to be run by a Celery worker.
    """
    logger.info(f"Starting sync flow for user: {user_id}")
    # Initialize services
    github_service = GitHubService()
    linkedin_service = LinkedInService()
    portfolio_agent = PortfolioAgent()
    
    # Collect data from all sources
    raw_data = {}
    
    # GitHub
    try:
        profile_task = github_service.get_user_profile(user_id)
        repos_task = github_service.get_repositories(user_id)
        github_data, github_repos = await asyncio.gather(profile_task, repos_task)
        raw_data['github'] = {'profile': github_data, 'repositories': github_repos}
        logger.info(f"Successfully fetched GitHub data for {user_id}")
    except Exception as e:
        logger.error(f"GitHub sync failed for {user_id}: {str(e)}")
    
    # LinkedIn
    try:
        await linkedin_service.initialize()
        linkedin_data = await linkedin_service.get_profile_data()
        raw_data['linkedin'] = linkedin_data
        logger.info(f"Successfully fetched LinkedIn data for {user_id}")
    except Exception as e:
        logger.error(f"LinkedIn sync failed for {user_id}: {str(e)}")
    finally:
        if linkedin_service:
            await linkedin_service.close()
    
    # Process with AI agent
    logger.info(f"Processing raw data with AI agent for {user_id}")
    processed_data = await portfolio_agent.process_raw_data(raw_data)
    
    # Save to database
    if not processed_data:
        logger.error(f"AI processing failed for {user_id}. No data to save.")
        return {}

    with get_db_session() as db:
        portfolio = db.query(Portfolio).filter_by(user_id=user_id).first()
        if not portfolio:
            portfolio = Portfolio(user_id=user_id)
            db.add(portfolio)
        
        portfolio.name = processed_data.get('profile', {}).get('name')
        portfolio.headline = processed_data.get('profile', {}).get('headline')
        portfolio.avatar_url = processed_data.get('profile', {}).get('avatar_url')
        portfolio.experience = processed_data.get('experience', [])
        portfolio.projects = processed_data.get('projects', [])
        portfolio.education = processed_data.get('education', [])
        portfolio.certifications = processed_data.get('certifications', [])
        portfolio.skills = processed_data.get('skills', [])
        portfolio.last_synced = datetime.utcnow()
        portfolio.sync_status = 'success'
        
        db.commit()
        logger.info(f"Successfully saved portfolio for user: {user_id}")
    
    return processed_data


@celery_app.task(name="tasks.sync_portfolio_task")
def sync_portfolio_task(user_id: str):
    """Celery task to run the sync flow."""
    return asyncio.run(run_sync_flow(user_id))


class SyncService:
    """Service for triggering synchronization tasks."""
    
    async def trigger_sync(self, user_id: str, source: str):
        """Triggers a background sync task."""
        logger.info(f"Triggering background sync for user {user_id} from source {source}")
        sync_portfolio_task.delay(user_id)