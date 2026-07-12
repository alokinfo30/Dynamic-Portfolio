# Dynamic-Portfolio
dynamic portfolio web application using the REHALT framework, CrewAI, and OpenRouter with strict JSON Schema validation.


DynamicPortfolio/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── config.py
│   ├── database.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── github_service.py
│   │   ├── linkedin_service.py
│   │   ├── resume_service.py
│   │   └── sync_service.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── github_agent.py
│   │   ├── linkedin_agent.py
│   │   ├── resume_agent.py
│   │   └── portfolio_agent.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── webhooks.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       └── logger.py
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── components.js
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── .env
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── Procfile
├── runtime.txt
└── README.md


# Dynamic Portfolio with REHALT Framework

A production-ready dynamic portfolio web application that aggregates data from GitHub, LinkedIn, and resume sources with AI-powered processing.

## Features

- 🔄 **Real-time Sync**: Automatically updates when data changes
- 🧠 **AI-Powered Processing**: Uses CrewAI and OpenRouter for data structuring
- 📊 **Multiple Sources**: GitHub, LinkedIn, and Resume integration
- 🎨 **Modern UI**: Clean bento-box design with responsive layout
- 🔒 **Secure**: Environment-based configuration with proper validation
- 📈 **Scalable**: Built with REHALT framework principles

## Architecture

### REHALT Framework Implementation

- **R - Requirements**: Dynamic portfolio with real-time updates
- **E - Estimation**: 1000 QPS, 10GB storage, 100k daily users
- **H - High-Level Design**: API Gateway, Core Services, Data Layer
- **A - Architecture (Data)**: PostgreSQL with Redis caching
- **L - Low-Level Design**: Connection pooling, caching, async queues
- **T - Trade-offs**: CAP compromise (Availability & Partition Tolerance)

### Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask + SQLAlchemy |
| Database | PostgreSQL / SQLite |
| AI/ML | CrewAI + OpenRouter |
| Cache | Redis |
| Queue | Celery |
| Frontend | HTML + CSS + JavaScript |
| Deployment | Docker + Gunicorn |

## Installation

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd DynamicPortfolio

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your configurations
cp .env.example .env

# Initialize database
python -c "from app.database import init_db; init_db()"

# Run application
python -m app.main




Docker Deployment
bash
# Build and run with Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t dynamic-portfolio .
docker run -p 5000:5000 dynamic-portfolio



Configuration
Environment Variables
Variable	Description
OPENROUTER_API_KEY	Your OpenRouter API key
GITHUB_TOKEN	GitHub Personal Access Token
LINKEDIN_EMAIL	LinkedIn account email
LINKEDIN_PASSWORD	LinkedIn account password
DATABASE_URL	Database connection URL
SECRET_KEY	Application secret key
API Endpoints
Endpoint	Method	Description
/api/health	GET	Health check
/api/portfolio/<user_id>	GET	Get portfolio
/api/sync	POST	Trigger sync
/api/webhook/github	POST	GitHub webhook
/api/webhook/linkedin	POST	LinkedIn webhook
/api/stats	GET	System statistics
Development
Running Tests
bash
pytest tests/ -v --cov=app
Code Formatting
bash
black app/
isort app/
Pre-commit Hooks
bash
pre-commit install
pre-commit run --all-files


Security Best Practices
Never commit .env files

Use environment variables for sensitive data

Enable HTTPS in production

Implement rate limiting

Validate all input data

Use proper CORS configuration

Contributing
Fork the repository

Create a feature branch

Make your changes

Submit a pull request



License
MIT

text

## Summary

This complete production-ready Dynamic Portfolio application includes:

### ✅ REHALT Framework Implementation:
- **Requirements**: Clear functional and non-functional requirements
- **Estimation**: Scale, QPS, and storage calculations
- **High-Level Design**: API Gateway, Core Services architecture
- **Architecture**: PostgreSQL with Redis caching, proper data models
- **Low-Level Design**: Connection pooling, async queues, rate limiting
- **Trade-offs**: CAP theorem considerations

### ✅ Features:
- GitHub, LinkedIn, Resume integration
- AI-powered data processing with CrewAI
- OpenRouter with `openrouter/free` model
- Strict JSON schema validation
- Real-time webhook updates
- Modern responsive UI
- Production-ready deployment

### ✅ Security:
- Environment-based configuration
- Input validation with Pydantic
- CORS and rate limiting
- Secure error handling

The application is ready for both local development and production deployment!