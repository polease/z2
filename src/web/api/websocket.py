"""
WebSocket endpoints for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..services.websocket_manager import manager
from ..services.job_service import JobService

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/jobs/status")
async def websocket_status_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time job status updates

    Broadcasts status changes to all connected clients
    """
    await manager.connect_status(websocket)
    try:
        # Keep connection alive
        while True:
            # Wait for any message from client (heartbeat)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_status(websocket)


@router.websocket("/ws/jobs/{job_uuid}/logs")
async def websocket_logs_endpoint(
    websocket: WebSocket,
    job_uuid: UUID,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for streaming job logs

    Sends historical logs on connect, then streams new logs in real-time
    """
    # Get job
    job = JobService.get_job_by_uuid(db, job_uuid)
    if not job:
        await websocket.close(code=1008, reason="Job not found")
        return

    await manager.connect_logs(job.id, websocket)

    try:
        # Send historical logs
        logs = JobService.get_logs(db, job.id)
        for log in logs:
            await websocket.send_json({
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "stage": log.stage,
                "message": log.message
            })

        # Keep connection alive and listen for new logs
        while True:
            # Wait for any message from client (heartbeat)
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect_logs(job.id, websocket)
