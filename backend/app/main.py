from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.contents import router as contents_router
from app.models.database import Base
from app.database import engine
import time
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    max_retries = 3
    retry_delay = 1

    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise Exception(f"Database connection failed after {max_retries} retries. Check DATABASE_URL configuration.")

    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (if needed)

app = FastAPI(title="History Storyteller API", lifespan=lifespan)

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
    return {"status": "ok"}

@app.get("/health/ready")
async def health_ready():
    from app.services.ai_service import ai_service
    from sqlalchemy import text
    from fastapi.responses import JSONResponse

    health_status = {"status": "ok", "checks": {}}
    is_ready = True

    # Check database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        is_ready = False
        health_status["status"] = "not_ready"
        health_status["checks"]["database"] = "failed"

    # Check AI providers
    if len(ai_service.providers) == 0:
        is_ready = False
        health_status["status"] = "not_ready"
        health_status["checks"]["ai_providers"] = "none_configured"
    else:
        health_status["checks"]["ai_providers"] = list(ai_service.providers.keys())

    status_code = 200 if is_ready else 503
    return JSONResponse(content=health_status, status_code=status_code)
