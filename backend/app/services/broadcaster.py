import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import WebSocket

from app.services.occupancy_service import get_occupancy_status

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSockets and SSE listener queues for real-time broadcasts."""

    def __init__(self) -> None:
        self.active_websockets: List[WebSocket] = []
        self.active_sse_queues: List[asyncio.Queue] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def register_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Register the primary asyncio event loop."""
        self._loop = loop

    async def connect_ws(self, websocket: WebSocket) -> None:
        """Accept and register an active WebSocket connection."""
        await websocket.accept()
        self.active_websockets.append(websocket)
        logger.info("WebSocket client connected. Active connections: %d", len(self.active_websockets))

    def disconnect_ws(self, websocket: WebSocket) -> None:
        """Unregister a disconnected WebSocket."""
        if websocket in self.active_websockets:
            self.active_websockets.remove(websocket)
            logger.info("WebSocket client disconnected. Active connections: %d", len(self.active_websockets))

    def connect_sse(self) -> asyncio.Queue:
        """Create and register a new SSE event queue."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self.active_sse_queues.append(queue)
        logger.info("SSE client connected. Active SSE listeners: %d", len(self.active_sse_queues))
        return queue

    def disconnect_sse(self, queue: asyncio.Queue) -> None:
        """Unregister a closed SSE event queue."""
        if queue in self.active_sse_queues:
            self.active_sse_queues.remove(queue)
            logger.info("SSE client disconnected. Active SSE listeners: %d", len(self.active_sse_queues))

    async def broadcast(self, payload: Dict[str, Any]) -> None:
        """Deliver the payload to all active WebSockets and SSE queues."""
        # 1. WebSockets broadcast
        dead_ws = []
        for ws in list(self.active_websockets):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception as exc:
                logger.debug("Failed to send WebSocket message: %s", exc)
                dead_ws.append(ws)

        for ws in dead_ws:
            self.disconnect_ws(ws)

        # 2. SSE Queues broadcast
        dead_queues = []
        for q in list(self.active_sse_queues):
            try:
                if q.full():
                    try:
                        q.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                q.put_nowait(payload)
            except Exception as exc:
                logger.debug("Failed to push to SSE queue: %s", exc)
                dead_queues.append(q)

        for q in dead_queues:
            self.disconnect_sse(q)


realtime_manager = ConnectionManager()


def get_current_state_payload(event_type: str = "initial_state", dining_hall: str = "Central Mess") -> Dict[str, Any]:
    """Build a standard payload containing current occupancy and metrics."""
    status_obj = get_occupancy_status(dining_hall=dining_hall)
    return {
        "event": "occupancy_update",
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "diningHall": dining_hall,
        "occupancy": {
            "totalSeats": status_obj.totalSeats,
            "occupiedSeats": status_obj.occupiedSeats,
            "availableSeats": status_obj.availableSeats,
            "occupancyPercentage": status_obj.occupancyPercentage,
            "crowdLevel": status_obj.crowdLevel,
            "mealType": status_obj.mealType,
            "updatedAt": status_obj.updatedAt,
        },
    }


def broadcast_occupancy_change(
    event_type: str,
    seat_number: Optional[int] = None,
    seat_status: Optional[str] = None,
    dining_hall: Optional[str] = "Central Mess",
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Safe thread-and-async dispatcher for occupancy change events."""
    payload = get_current_state_payload(event_type, dining_hall or "Central Mess")
    if seat_number is not None:
        payload["seatNumber"] = seat_number
    if seat_status is not None:
        payload["seatStatus"] = seat_status
    if extra:
        payload.update(extra)

    # Schedule async broadcast task safely
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(realtime_manager.broadcast(payload))
    except RuntimeError:
        # No running loop in current thread
        if realtime_manager._loop and realtime_manager._loop.is_running():
            asyncio.run_coroutine_threadsafe(realtime_manager.broadcast(payload), realtime_manager._loop)
        else:
            logger.debug("No active event loop available to broadcast: %s", event_type)
