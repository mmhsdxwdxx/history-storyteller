from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.contents import router as contents_router
from app.models.database import Base
from app.database import engine

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
