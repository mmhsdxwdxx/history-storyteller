from fastapi import APIRouter
from app.services.ai_service import ai_service
from app.schemas.schemas import ProviderInfoResponse

router = APIRouter(prefix="/api/providers", tags=["providers"])

@router.get("", response_model=ProviderInfoResponse)
async def get_providers():
    available = list(ai_service.providers.keys())
    default = ai_service.default_provider if ai_service.default_provider in available else None
    return {
        "available_providers": available,
        "default_provider": default
    }
