"""
WebSocket API for real-time updates.
"""

import asyncio
import json
from typing import Dict, Set
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Map project_id -> set of connected websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """Accept connection and add to project's connection set."""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """Remove connection from project's connection set."""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            
            # Cleanup empty sets
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
    
    async def send_to_project(self, project_id: str, message: dict):
        """Send message to all connections for a project."""
        if project_id not in self.active_connections:
            return
        
        disconnected = set()
        for websocket in self.active_connections[project_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.active_connections[project_id].discard(ws)
    
    async def broadcast_progress(
        self,
        project_id: str,
        progress_type: str,
        progress: float,
        message: str = None
    ):
        """Broadcast progress update to all project connections."""
        await self.send_to_project(project_id, {
            "type": progress_type,
            "progress": progress,
            "message": message,
        })
    
    async def broadcast_status_change(self, project_id: str, status: str):
        """Broadcast status change to all project connections."""
        await self.send_to_project(project_id, {
            "type": "status_change",
            "status": status,
        })


# Global connection manager
manager = ConnectionManager()


@router.websocket("/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time project updates.
    
    Clients connect to receive:
    - transcription_progress: {progress: 0-100, message: str}
    - render_progress: {progress: 0-100, message: str}
    - status_change: {status: str}
    - error: {message: str}
    """
    await manager.connect(websocket, project_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "project_id": project_id,
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                # Wait for any client messages (ping/pong, etc.)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # Handle ping
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, project_id)


# Helper functions for other modules to send updates
async def send_transcription_progress(project_id: str, progress: float, message: str = None):
    """Send transcription progress update."""
    await manager.broadcast_progress(project_id, "transcription_progress", progress, message)


async def send_render_progress(project_id: str, progress: float, message: str = None):
    """Send render progress update."""
    await manager.broadcast_progress(project_id, "render_progress", progress, message)


async def send_status_change(project_id: str, status: str):
    """Send status change notification."""
    await manager.broadcast_status_change(project_id, status)


async def send_error(project_id: str, error_message: str):
    """Send error notification."""
    await manager.send_to_project(project_id, {
        "type": "error",
        "message": error_message,
    })
