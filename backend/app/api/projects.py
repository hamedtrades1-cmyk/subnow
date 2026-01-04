"""
Projects API endpoints.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    return []


@router.get("/{project_id}")
def get_project(project_id: UUID, db: Session = Depends(get_db)):
    return {"id": str(project_id), "title": "Test Project", "status": "ready"}


@router.post("/")
def create_project(db: Session = Depends(get_db)):
    return {"id": "123", "title": "New Project", "status": "created"}
