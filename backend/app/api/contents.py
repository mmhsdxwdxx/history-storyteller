from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import Content, ContentVersion, ContentStatus
from app.schemas.schemas import ContentCreate, ContentUpdate
from app.services.ai_service import ai_service
from app.database import get_db

router = APIRouter(prefix="/api/contents", tags=["contents"])

@router.post("/")
async def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    db_content = Content(title=content.title, original_text=content.original_text)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

@router.get("/")
async def list_contents(db: Session = Depends(get_db)):
    return db.query(Content).all()

@router.get("/{content_id}")
async def get_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.post("/{content_id}/process")
async def process_content(content_id: int, provider: str = None, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content.status = ContentStatus.PROCESSING
    db.commit()

    try:
        vernacular = await ai_service.translate_to_vernacular(content.original_text, provider)
        content.vernacular_text = vernacular

        version = ContentVersion(content_id=content_id, version_number=1, field_name="vernacular_text", field_value=vernacular)
        db.add(version)

        humorous = await ai_service.create_humorous_version(vernacular, provider)
        content.humorous_text = humorous

        version2 = ContentVersion(content_id=content_id, version_number=1, field_name="humorous_text", field_value=humorous)
        db.add(version2)

        content.status = ContentStatus.COMPLETED
        db.commit()
        db.refresh(content)
        return content
    except Exception as e:
        content.status = ContentStatus.DRAFT
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))
