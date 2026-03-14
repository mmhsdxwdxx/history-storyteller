from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.contents import router as contents_router
from app.models.database import Base
from app.database import engine
import time
from sqlalchemy import text

def wait_for_db():
    max_retries = 30
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                raise

wait_for_db()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="History Storyteller API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contents_router)

@app.get("/")
async def root():
    return {"message": "History Storyteller API"}

@app.get("/health")
async def health():
    from app.services.ai_service import ai_service
    from sqlalchemy import text

    health_status = {"status": "ok", "checks": {}}

    # Check database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["database"] = "failed"

    # Check AI providers
    if len(ai_service.providers) == 0:
        health_status["status"] = "degraded"
        health_status["checks"]["ai_providers"] = "none_configured"
    else:
        health_status["checks"]["ai_providers"] = list(ai_service.providers.keys())

    return health_status
