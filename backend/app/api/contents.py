from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import Content, ContentVersion, ContentStatus, GenerationResult
from app.schemas.schemas import ContentCreate, ContentUpdate, ContentResponse, GenerationResultResponse, ErrorResponse
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
    contents = db.query(Content).all()
    # 为每个内容添加最新生成结果
    for content in contents:
        content.latest_generation = content.generations[0] if content.generations else None
    return contents

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    content.latest_generation = content.generations[0] if content.generations else None
    return content

@router.get("/{content_id}/generations", response_model=List[GenerationResultResponse])
async def get_generations(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content.generations

@router.post("/{content_id}/process", response_model=GenerationResultResponse, responses={
    404: {"model": ErrorResponse, "description": "Content not found"},
    409: {"model": ErrorResponse, "description": "Content is already being processed"},
    422: {"model": ErrorResponse, "description": "AI provider configuration error"},
    500: {"model": ErrorResponse, "description": "Processing failed"}
})
async def process_content(content_id: int, provider: str = None, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.status == ContentStatus.PROCESSING:
        raise HTTPException(status_code=409, detail="Content is already being processed")

    content.status = ContentStatus.PROCESSING
    db.commit()

    try:
        vernacular = await ai_service.translate_to_vernacular(content.original_text, provider)
        humorous = await ai_service.create_humorous_version(vernacular, provider)

        # 获取实际使用的 provider
        actual_provider = provider or ai_service.default_provider or list(ai_service.providers.keys())[0]

        # 创建新的生成结果
        generation = GenerationResult(
            content_id=content_id,
            provider=actual_provider,
            vernacular_text=vernacular,
            humorous_text=humorous
        )
        db.add(generation)

        content.status = ContentStatus.COMPLETED
        db.commit()
        db.refresh(generation)
        return generation
    except ValueError as e:
        db.rollback()
        content = db.query(Content).filter(Content.id == content_id).first()
        content.status = ContentStatus.DRAFT
        db.commit()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        content = db.query(Content).filter(Content.id == content_id).first()
        content.status = ContentStatus.DRAFT
        db.commit()
        raise HTTPException(status_code=500, detail="Processing failed")
