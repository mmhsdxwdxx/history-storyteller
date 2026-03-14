from pydantic import BaseModel
from typing import Optional

class ContentCreate(BaseModel):
    title: str
    original_text: str

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
