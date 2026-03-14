from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import Content, ContentVersion, ContentStatus
from app.schemas.schemas import ContentCreate, ContentUpdate, ContentResponse
from app.services.ai_service import ai_service
from app.database import get_db

router = APIRouter(prefix="/api/contents", tags=["contents"])

@router.post("", response_model=ContentResponse)
async def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    db_content = Content(title=content.title, original_text=content.original_text)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

@router.get("", response_model=List[ContentResponse])
async def list_contents(db: Session = Depends(get_db)):
    return db.query(Content).all()

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.post("/{content_id}/process", response_model=ContentResponse)
async def process_content(content_id: int, provider: str = None, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.status == ContentStatus.PROCESSING:
        raise HTTPException(status_code=409, detail="Content is already being processed")

    old_status = content.status
    old_vernacular = content.vernacular_text
    old_humorous = content.humorous_text

    content.status = ContentStatus.PROCESSING
    db.commit()

    try:
        vernacular = await ai_service.translate_to_vernacular(content.original_text, provider)
        humorous = await ai_service.create_humorous_version(vernacular, provider)

        version_count = db.query(ContentVersion).filter(ContentVersion.content_id == content_id).count()

        content.vernacular_text = vernacular
        content.humorous_text = humorous
        content.status = ContentStatus.COMPLETED

        version1 = ContentVersion(content_id=content_id, version_number=version_count + 1, field_name="vernacular_text", field_value=vernacular)
        version2 = ContentVersion(content_id=content_id, version_number=version_count + 2, field_name="humorous_text", field_value=humorous)
        db.add(version1)
        db.add(version2)

        db.commit()
        db.refresh(content)
        return content
    except ValueError as e:
        db.rollback()
        content = db.query(Content).filter(Content.id == content_id).first()
        content.status = old_status
        db.commit()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        content = db.query(Content).filter(Content.id == content_id).first()
        content.status = old_status
        content.vernacular_text = old_vernacular
        content.humorous_text = old_humorous
        db.commit()
        raise HTTPException(status_code=500, detail="Processing failed")
