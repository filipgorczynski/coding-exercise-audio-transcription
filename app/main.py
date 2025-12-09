from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import transcriptions
from config import settings

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)
app.include_router(
    transcriptions.router, prefix="/api/transcriptions", tags=["transcriptions"]
)


@app.get("/")
async def root():
    return {
        "message": "Audio/Video Transcription API",
        "docs": "/docs",
        "version": settings.API_VERSION,
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}
