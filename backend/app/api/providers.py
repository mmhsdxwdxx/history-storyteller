from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.services.ai_service import ai_service
from app.schemas.schemas import ProviderInfoResponse, ProviderConfigCreate, ProviderConfigResponse
from app.models.database import ProviderConfig
from app.database import get_db

router = APIRouter(prefix="/api/providers", tags=["providers"])

@router.get("", response_model=ProviderInfoResponse)
async def get_providers():
    available = list(ai_service.providers.keys())
    default = ai_service.default_provider if ai_service.default_provider in available else None
    return {
        "available_providers": available,
        "default_provider": default
    }

@router.get("/configs", response_model=List[ProviderConfigResponse])
async def get_provider_configs(db: Session = Depends(get_db)):
    """获取所有保存的 provider 配置"""
    return db.query(ProviderConfig).all()

@router.post("/configs", response_model=ProviderConfigResponse)
async def save_provider_config(config: ProviderConfigCreate, db: Session = Depends(get_db)):
    """保存或更新 provider 配置"""
    existing = db.query(ProviderConfig).filter(
        ProviderConfig.provider_name == config.provider_name
    ).first()

    if existing:
        existing.api_url = config.api_url
        existing.api_key = config.api_key
        existing.model = config.model
        if config.is_default:
            db.query(ProviderConfig).update({ProviderConfig.is_default: False})
        existing.is_default = 1 if config.is_default else 0
        db.commit()
        db.refresh(existing)
        return existing
    else:
        if config.is_default:
            db.query(ProviderConfig).update({ProviderConfig.is_default: False})
        new_config = ProviderConfig(
            provider_name=config.provider_name,
            api_url=config.api_url,
            api_key=config.api_key,
            model=config.model,
            is_default=1 if config.is_default else 0
        )
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return new_config

@router.post("/reload")
async def reload_providers(db: Session = Depends(get_db)):
    """重新加载 provider 配置"""
    from app.services.ai_service import AIService
    global ai_service
    ai_service = AIService(db)
    return {"message": "Providers reloaded", "available": list(ai_service.providers.keys())}
