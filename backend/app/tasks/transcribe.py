"""
Transcription Celery tasks.
"""

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True)
def transcribe_video_task(self, project_id: str, video_path: str, language: str = "en"):
    """
    Async task to transcribe a video.
    """
    # Placeholder - will implement later
    return {"status": "completed", "project_id": project_id}
