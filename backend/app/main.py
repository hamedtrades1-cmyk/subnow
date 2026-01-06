"""
CaptionMagic - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api import api_router

app = FastAPI(
    title=settings.app_name,
    description="Open-source video captioning with animated subtitles",
    version="0.1.0",
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
