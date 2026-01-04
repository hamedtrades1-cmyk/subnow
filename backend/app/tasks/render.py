"""
Video rendering Celery tasks.
"""

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True)
def render_video_task(self, project_id: str, video_path: str, ass_path: str):
    """
    Async task to render video with captions.
    """
    # Placeholder - will implement later
    return {"status": "completed", "project_id": project_id}
