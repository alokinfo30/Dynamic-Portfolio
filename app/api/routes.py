# app/api/routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from typing import Dict, Any
import logging
from datetime import datetime
import asyncio

from app.database import get_db_session
from app.models import User, Portfolio, SyncLog
from app.schemas import (
    PortfolioStateSchema,
    SyncRequestSchema,
    WebhookPayloadSchema
)
from app.services.github_service import GitHubService
from app.services.linkedin_service import LinkedInService
from app.services.sync_service import SyncService, sync_portfolio_task
from app.agents.portfolio_agent import PortfolioAgent

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@api_bp.route('/portfolio/<user_id>', methods=['GET'])
@cross_origin()
def get_portfolio(user_id: str):
    """Get portfolio by user ID"""
    try:
        with get_db_session() as db:
            portfolio = db.query(Portfolio).filter_by(user_id=user_id).first()
            if not portfolio:
                return jsonify({'error': 'Portfolio not found'}), 404
            
            return jsonify({
                'status': 'success',
                'data': {
                    'profile': {
                        'name': portfolio.name,
                        'headline': portfolio.headline,
                        'avatar_url': portfolio.avatar_url
                    },
                    'experience': portfolio.experience,
                    'projects': portfolio.projects,
                    'education': portfolio.education,
                    'certifications': portfolio.certifications,
                    'skills': portfolio.skills,
                    'last_synced': portfolio.last_synced.isoformat() if portfolio.last_synced else None
                }
            })
            
    except Exception as e:
        logger.error(f"Error fetching portfolio: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/sync', methods=['POST'])
@cross_origin()
def sync_portfolio(): # This remains a sync function
    """Sync portfolio data from all sources"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Trigger the background task
        sync_portfolio_task.delay(user_id)
        
        return jsonify({
            'status': 'pending',
            'message': 'Portfolio sync has been started in the background.'
        }), 202
            
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/webhook/github', methods=['POST'])
@cross_origin()
async def github_webhook():
    """GitHub webhook endpoint"""
    try:
        data = request.json
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        
        user_id = data.get('repository', {}).get('owner', {}).get('login')

        # Process webhook and trigger sync asynchronously
        processed = await process_github_webhook(data, user_id)
        
        return jsonify({
            'status': 'received',
            'event': event_type,
            'processed': processed
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

async def process_github_webhook(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Helper to process webhook and trigger sync."""
    github_service = GitHubService()
    processed = await github_service.process_webhook(data)
    
    if user_id:
        # Trigger async sync
        sync_service = SyncService()
        await sync_service.trigger_sync(user_id, 'github')
    return processed


@api_bp.route('/webhook/linkedin', methods=['POST'])
@cross_origin()
async def linkedin_webhook():
    """LinkedIn webhook endpoint"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if user_id: # This can be done in the background
            sync_service = SyncService()
            await sync_service.trigger_sync(user_id, 'linkedin')
        
        return jsonify({
            'status': 'received',
            'message': 'LinkedIn sync triggered'
        })
        
    except Exception as e:
        logger.error(f"LinkedIn webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """Get system statistics"""
    try:
        with get_db_session() as db:
            portfolio_count = db.query(Portfolio).count()
            sync_log_count = db.query(SyncLog).count()
            recent_syncs = db.query(SyncLog).order_by(
                SyncLog.created_at.desc()
            ).limit(10).all()
            
            return jsonify({
                'status': 'success',
                'stats': {
                    'total_portfolios': portfolio_count,
                    'total_syncs': sync_log_count,
                    'recent_syncs': [
                        {
                            'source': log.source,
                            'status': log.status,
                            'created_at': log.created_at.isoformat()
                        }
                        for log in recent_syncs
                    ]
                }
            })
            
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500