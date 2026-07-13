import importlib
import os

import pytest


@pytest.fixture
def config_module(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,https://example.com")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("CELERY_BROKER_URL", raising=False)
    monkeypatch.delenv("CELERY_RESULT_BACKEND", raising=False)
    import app.config as config
    return importlib.reload(config)


def test_comma_separated_cors_origins_are_parsed(config_module):
    settings = config_module.Settings()
    assert settings.get_cors_allowed_origins() == ["http://localhost:3000", "https://example.com"]
