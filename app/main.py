# app/main.py
import os
import logging
from flask import Flask, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import sentry_sdk

from app.config import settings
from app.database import init_db
from app.api.routes import api_bp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Sentry if configured
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        release=settings.APP_NAME
    )


def create_app():
    """Application factory"""
    app = Flask(__name__, 
                template_folder='../frontend',
                static_folder='../frontend/static')
    
    # Configuration
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_REQUEST_SIZE
    
    # CORS
    CORS(app, origins=settings.CORS_ALLOWED_ORIGINS)
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT]
    )
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Initialize database
    with app.app_context():
        init_db()
        logger.info("Database initialized")
    
    # Routes
    @app.route('/')
    def index():
        """Serve frontend"""
        return render_template('index.html')
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {str(error)}")
        return {'error': 'Internal server error'}, 500
    
    logger.info(f"Application started in {settings.APP_ENV} mode")
    
    return app


# Create application instance
app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=settings.PORT,
        debug=settings.DEBUG
    )