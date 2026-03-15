from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import Content, ContentStatus, GenerationResult, ContentVersion
from app.schemas.schemas import ContentCreate, ContentResponse, GenerationResultResponse, ErrorResponse
from app.services.ai_service import ai_service
from app.database import get_db

router = APIRouter(prefix="/api/contents", tags=["contents"])

def get_effective_generation(content: Content):
    """获取有效生成结果，优先使用新版generation_results，兼容旧数据"""
    if content.generations:
        return content.generations[0]
    # 旧数据兼容：如果没有 generations 但有旧字段，创建虚拟 generation
    if content.vernacular_text or content.humorous_text:
        return {
            "id": 0,
            "provider": content.legacy_provider or "legacy",
            "vernacular_text": content.vernacular_text,
            "humorous_text": content.humorous_text,
            "created_at": content.updated_at
        }
    return None

def get_all_generations(content: Content):
    """获取所有生成结果，包含旧数据兼容"""
    if content.generations:
        return content.generations
    # 旧数据兼容：如果没有 generations 但有旧字段，返回兼容的 generation
    if content.vernacular_text or content.humorous_text:
        return [{
            "id": 0,
            "provider": content.legacy_provider or "legacy",
            "vernacular_text": content.vernacular_text,
            "humorous_text": content.humorous_text,
            "created_at": content.updated_at
        }]
    return []

@router.post("", response_model=ContentResponse)
async def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    db_content = Content(title=content.title, original_text=content.original_text)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    db_content.latest_generation = None
    return db_content

@router.get("", response_model=List[ContentResponse])
async def list_contents(db: Session = Depends(get_db)):
    contents = db.query(Content).all()
    for content in contents:
        content.latest_generation = get_effective_generation(content)
        content.generations = get_all_generations(content)
    return contents

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    content.latest_generation = get_effective_generation(content)
    content.generations = get_all_generations(content)
    return content

@router.get("/{content_id}/generations", response_model=List[GenerationResultResponse])
async def get_generations(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    # 如果没有 generations 但有旧数据，返回兼容的 generation
    if not content.generations and (content.vernacular_text or content.humorous_text):
        return [{
            "id": 0,
            "provider": content.legacy_provider or "legacy",
            "vernacular_text": content.vernacular_text,
            "humorous_text": content.humorous_text,
            "created_at": content.updated_at
        }]
    return content.generations

@router.post("/{content_id}/migrate", response_model=GenerationResultResponse)
async def migrate_legacy_data(content_id: int, db: Session = Depends(get_db)):
    """将旧数据迁移到新的 generation_results 表"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if not content.vernacular_text and not content.humorous_text:
        raise HTTPException(status_code=400, detail="No legacy data to migrate")
    if content.generations:
        raise HTTPException(status_code=400, detail="Already migrated")

    generation = GenerationResult(
        content_id=content_id,
        provider=content.legacy_provider or "legacy",
        vernacular_text=content.vernacular_text,
        humorous_text=content.humorous_text
    )
    db.add(generation)
    db.commit()
    db.refresh(generation)
    return generation

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

    # 保存旧状态，失败时恢复
    old_status = content.status
    content.status = ContentStatus.PROCESSING
    db.commit()

    try:
        vernacular = await ai_service.translate_to_vernacular(content.original_text, provider)
        humorous = await ai_service.create_humorous_version(vernacular, provider)

        # 获取实际使用的 provider
        actual_provider = provider or ai_service.default_provider
        if not actual_provider and ai_service.providers:
            actual_provider = list(ai_service.providers.keys())[0]

        # 创建新的生成结果
        generation = GenerationResult(
            content_id=content_id,
            provider=actual_provider,
            vernacular_text=vernacular,
            humorous_text=humorous
        )
        db.add(generation)

        # 写入版本记录
        version_count = db.query(ContentVersion).filter(ContentVersion.content_id == content_id).count()
        v1 = ContentVersion(
            content_id=content_id,
            version_number=version_count + 1,
            field_name=f"vernacular_text_{actual_provider}",
            field_value=vernacular
        )
        v2 = ContentVersion(
            content_id=content_id,
            version_number=version_count + 2,
            field_name=f"humorous_text_{actual_provider}",
            field_value=humorous
        )
        db.add(v1)
        db.add(v2)

        content.status = ContentStatus.COMPLETED
        db.commit()
        db.refresh(generation)
        return generation
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
        db.commit()
        raise HTTPException(status_code=500, detail="Processing failed")
