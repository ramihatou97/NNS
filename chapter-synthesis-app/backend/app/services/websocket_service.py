import asyncio
import json
from typing import Dict, Set
import socketio
from app.core.config import settings

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.BACKEND_CORS_ORIGINS,
    logger=settings.DEBUG,
    engineio_logger=settings.DEBUG
)

# Track connected clients
connected_clients: Dict[str, Set[str]] = {}  # {user_id: {session_id, session_id, ...}}


@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    print(f"Client connected: {sid}")

    # Extract user info from auth
    user_id = auth.get("user_id") if auth else None

    if user_id:
        if user_id not in connected_clients:
            connected_clients[user_id] = set()
        connected_clients[user_id].add(sid)

        await sio.emit("connected", {"sid": sid, "user_id": user_id}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    print(f"Client disconnected: {sid}")

    # Remove from connected clients
    for user_id, sessions in connected_clients.items():
        if sid in sessions:
            sessions.remove(sid)
            break


@sio.event
async def subscribe_to_job(sid, data):
    """Subscribe to job updates"""
    job_id = data.get("job_id")
    if job_id:
        await sio.enter_room(sid, f"job:{job_id}")
        await sio.emit("subscribed", {"job_id": job_id}, room=sid)


@sio.event
async def unsubscribe_from_job(sid, data):
    """Unsubscribe from job updates"""
    job_id = data.get("job_id")
    if job_id:
        await sio.leave_room(sid, f"job:{job_id}")
        await sio.emit("unsubscribed", {"job_id": job_id}, room=sid)


class WebSocketService:
    """Service for managing WebSocket communications"""

    @staticmethod
    async def emit_to_user(user_id: str, event: str, data: dict):
        """Emit event to all sessions of a user"""
        if user_id in connected_clients:
            for sid in connected_clients[user_id]:
                await sio.emit(event, data, room=sid)

    @staticmethod
    async def emit_to_job(job_id: str, event: str, data: dict):
        """Emit event to all subscribers of a job"""
        await sio.emit(event, data, room=f"job:{job_id}")

    @staticmethod
    async def emit_indexing_progress(document_id: int, progress: float, stage: str, data: dict = None):
        """Emit indexing progress update"""
        await sio.emit("indexing_progress", {
            "document_id": document_id,
            "progress": progress,
            "stage": stage,
            "data": data or {}
        }, room=f"document:{document_id}")

    @staticmethod
    async def emit_generation_progress(
        job_id: str,
        progress: float,
        stage: str,
        data: dict = None
    ):
        """Emit chapter generation progress"""
        await sio.emit("generation_progress", {
            "job_id": job_id,
            "progress": progress,
            "stage": stage,
            "data": data or {}
        }, room=f"job:{job_id}")

    @staticmethod
    async def emit_section_chunk(job_id: str, section_title: str, chunk: str):
        """Emit incremental section chunk"""
        await sio.emit("section_chunk", {
            "job_id": job_id,
            "section_title": section_title,
            "chunk": chunk
        }, room=f"job:{job_id}")

    @staticmethod
    async def emit_dashboard_update(user_id: str, metrics: dict):
        """Emit dashboard metrics update"""
        await WebSocketService.emit_to_user(user_id, "dashboard_update", metrics)

    @staticmethod
    async def emit_notification(user_id: str, notification: dict):
        """Emit notification to user"""
        await WebSocketService.emit_to_user(user_id, "notification", notification)

    @staticmethod
    def get_connected_users() -> Set[str]:
        """Get set of connected user IDs"""
        return set(connected_clients.keys())

    @staticmethod
    def get_user_session_count(user_id: str) -> int:
        """Get number of active sessions for a user"""
        return len(connected_clients.get(user_id, set()))


# Create ASGI application
socket_app = socketio.ASGIApp(
    sio,
    socketio_path="/ws/socket.io"
)
