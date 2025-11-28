"""
WebSocket connection manager for broadcasting updates
"""
from fastapi import WebSocket
from typing import Dict, List, Set
from uuid import UUID
import json
import asyncio


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        # Active connections for status broadcasts
        self.active_connections: Set[WebSocket] = set()

        # Job-specific log connections
        self.log_connections: Dict[int, Set[WebSocket]] = {}

    async def connect_status(self, websocket: WebSocket):
        """Connect a client to status broadcasts"""
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect_status(self, websocket: WebSocket):
        """Disconnect a client from status broadcasts"""
        self.active_connections.discard(websocket)

    async def connect_logs(self, job_id: int, websocket: WebSocket):
        """Connect a client to job-specific logs"""
        await websocket.accept()
        if job_id not in self.log_connections:
            self.log_connections[job_id] = set()
        self.log_connections[job_id].add(websocket)

    def disconnect_logs(self, job_id: int, websocket: WebSocket):
        """Disconnect a client from job-specific logs"""
        if job_id in self.log_connections:
            self.log_connections[job_id].discard(websocket)
            if not self.log_connections[job_id]:
                del self.log_connections[job_id]

    async def broadcast_status(self, message: dict):
        """Broadcast status update to all connected clients"""
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.discard(connection)

    async def send_log(self, job_id: int, message: dict):
        """Send log message to all clients listening to this job"""
        if job_id not in self.log_connections:
            return

        disconnected = set()

        for connection in self.log_connections[job_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.log_connections[job_id].discard(connection)

        if not self.log_connections[job_id]:
            del self.log_connections[job_id]


# Global connection manager instance
manager = ConnectionManager()
