from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class ContentCreate(BaseModel):
    title: str
    original_text: str

    @field_validator('title', 'original_text')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()

class ContentResponse(BaseModel):
    id: int
    title: str
    original_text: str
    vernacular_text: Optional[str] = None
    humorous_text: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    original_text: Optional[str] = None
    vernacular_text: Optional[str] = None
    humorous_text: Optional[str] = None

class MaterialCreate(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None

class ScheduleCreate(BaseModel):
    content_id: int
    scheduled_date: str
