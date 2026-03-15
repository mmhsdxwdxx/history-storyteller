from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.contents import router as contents_router
from app.api.providers import router as providers_router
from app.models.database import Base
from app.database import engine
import asyncio
from sqlalchemy import text, inspect

def run_migrations():
    """运行数据库迁移，添加缺失的列"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('contents')]

    migrations = []
    if 'vernacular_text' not in columns:
        migrations.append("ALTER TABLE contents ADD COLUMN vernacular_text TEXT")
    if 'humorous_text' not in columns:
        migrations.append("ALTER TABLE contents ADD COLUMN humorous_text TEXT")
    if 'legacy_provider' not in columns:
        migrations.append("ALTER TABLE contents ADD COLUMN legacy_provider VARCHAR(50)")

    # 检查 generation_results 表是否存在
    if 'generation_results' not in inspector.get_table_names():
        migrations.append("""
            CREATE TABLE generation_results (
                id SERIAL PRIMARY KEY,
                content_id INTEGER NOT NULL REFERENCES contents(id),
                provider VARCHAR(50) NOT NULL,
                vernacular_text TEXT,
                humorous_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        migrations.append("CREATE INDEX IF NOT EXISTS ix_generation_results_content_id ON generation_results(content_id)")

    if migrations:
        with engine.connect() as conn:
            for sql in migrations:
                conn.execute(text(sql))
            conn.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    max_retries = 3
    retry_delay = 0.5

    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception as e:
            if i < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise Exception(f"Database connection failed after {max_retries} retries. Check DATABASE_URL configuration.")

    # 创建新表
    Base.metadata.create_all(bind=engine)

    # 运行迁移（添加缺失的列）
    try:
        run_migrations()
    except Exception as e:
        print(f"Migration warning: {e}")

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
app.include_router(providers_router)

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
