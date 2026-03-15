from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import Content, ContentStatus, GenerationResult, ContentVersion
from app.schemas.schemas import ContentCreate, ContentResponse, GenerationResultResponse, ErrorResponse
from app.services.ai_service import ai_service
from app.database import get_db

router = APIRouter(prefix="/api/contents", tags=["contents"])


def _build_generation_dict(gen: GenerationResult) -> dict:
    """将 GenerationResult ORM 对象转换为字典"""
    return {
        "id": gen.id,
        "provider": gen.provider,
        "vernacular_text": gen.vernacular_text,
        "humorous_text": gen.humorous_text,
        "created_at": gen.created_at
    }


def _build_legacy_generation(content: Content) -> Optional[dict]:
    """为旧数据构建兼容的 generation 字典"""
    if not content.vernacular_text and not content.humorous_text:
        return None
    return {
        "id": 0,
        "provider": content.legacy_provider or "legacy",
        "vernacular_text": content.vernacular_text,
        "humorous_text": content.humorous_text,
        "created_at": content.updated_at
    }


def _get_all_generations(content: Content) -> List[dict]:
    """获取所有生成结果的字典列表（不修改 ORM 对象）"""
    if content.generations:
        return [_build_generation_dict(g) for g in content.generations]
    legacy = _build_legacy_generation(content)
    return [legacy] if legacy else []


def _get_latest_generation(content: Content) -> Optional[dict]:
    """获取最新生成结果的字典（不修改 ORM 对象）"""
    if content.generations:
        return _build_generation_dict(content.generations[0])
    return _build_legacy_generation(content)


def _build_content_response(content: Content) -> dict:
    """构建 Content 响应字典（不修改 ORM 对象）"""
    return {
        "id": content.id,
        "title": content.title,
        "original_text": content.original_text,
        "status": content.status,
        "created_at": content.created_at,
        "updated_at": content.updated_at,
        "generations": _get_all_generations(content),
        "latest_generation": _get_latest_generation(content)
    }

@router.post("", response_model=ContentResponse)
async def create_content(content: ContentCreate, db: Session = Depends(get_db)):
    db_content = Content(title=content.title, original_text=content.original_text)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return _build_content_response(db_content)


@router.get("", response_model=List[ContentResponse])
async def list_contents(db: Session = Depends(get_db)):
    contents = db.query(Content).all()
    return [_build_content_response(c) for c in contents]


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return _build_content_response(content)

@router.get("/{content_id}/generations", response_model=List[GenerationResultResponse])
async def get_generations(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return _get_all_generations(content)

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
