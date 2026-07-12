# app/models.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, 
    JSON, Text, Boolean, ForeignKey, Table
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
import uuid

from app.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    sync_logs = relationship("SyncLog", back_populates="user")


class Portfolio(Base):
    """Portfolio model"""
    __tablename__ = "portfolios"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Profile
    name = Column(String(255), nullable=False)
    headline = Column(String(500))
    avatar_url = Column(String(1000))
    
    # Data
    experience = Column(JSONB, default=list)
    projects = Column(JSONB, default=list)
    skills = Column(JSONB, default=list)
    education = Column(JSONB, default=list)
    certifications = Column(JSONB, default=list)
    
    # Metadata
    last_synced = Column(DateTime, default=datetime.utcnow)
    sync_status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolio")
    sync_logs = relationship("SyncLog", back_populates="portfolio")


class SyncLog(Base):
    """Sync log model for tracking updates"""
    __tablename__ = "sync_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(String(36), ForeignKey("portfolios.id"), nullable=False)
    
    source = Column(String(50), nullable=False)  # github, linkedin, resume
    status = Column(String(50), nullable=False)  # pending, success, failed
    data = Column(JSONB)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sync_logs")
    portfolio = relationship("Portfolio", back_populates="sync_logs")


class WebhookEvent(Base):
    """Webhook event model"""
    __tablename__ = "webhook_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False)  # github, linkedin
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class CacheEntry(Base):
    """Cache entry model"""
    __tablename__ = "cache_entries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(255), unique=True, nullable=False)
    value = Column(JSONB)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)