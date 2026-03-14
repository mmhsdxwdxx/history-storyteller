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
    return {"status": "ok"}
