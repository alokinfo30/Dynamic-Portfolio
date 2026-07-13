# app/schemas.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ProfileSchema(BaseModel):
    """Profile schema with strict validation"""
    name: str = Field(..., min_length=1, max_length=255)
    headline: str = Field(..., max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=1000)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class ExperienceSchema(BaseModel):
    """Experience schema with strict validation"""
    company: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=255)
    duration: str = Field(..., max_length=100)
    bullets: List[str] = Field(default_factory=list)
    
    @validator('bullets')
    def validate_bullets(cls, v):
        return [b.strip() for b in v if b.strip()]


class ProjectSchema(BaseModel):
    """Project schema with strict validation"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=1000)
    stars: int = Field(0, ge=0)
    tech_stack: List[str] = Field(default_factory=list)
    url: Optional[str] = Field(None, max_length=1000)
    
    @validator('tech_stack')
    def validate_tech_stack(cls, v):
        return [t.strip() for t in v if t.strip()]


class EducationSchema(BaseModel):
    """Education schema"""
    institution: str = Field(..., min_length=1, max_length=255)
    degree: str = Field(..., max_length=255)
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None


class CertificationSchema(BaseModel):
    """Certification schema"""
    name: str = Field(..., min_length=1, max_length=255)
    issuer: str = Field(..., max_length=255)
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None


class PortfolioStateSchema(BaseModel):
    """Complete portfolio state with strict JSON schema"""
    profile: ProfileSchema
    experience: List[ExperienceSchema]
    projects: List[ProjectSchema]
    education: List[EducationSchema] = Field(default_factory=list)
    certifications: List[CertificationSchema] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    last_synced: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "required": ["profile", "experience", "projects"]
        }


class SyncRequestSchema(BaseModel):
    """Sync request schema"""
    source: str = Field(..., pattern=r"^(github|linkedin|resume)$")
    data: Dict[str, Any]
    user_id: Optional[str] = None


class WebhookPayloadSchema(BaseModel):
    """Webhook payload schema"""
    source: str = Field(..., pattern=r"^(github|linkedin)$")
    event_type: str
    payload: Dict[str, Any]
    timestamp: Optional[datetime] = None