import asyncio
from datetime import datetime, timezone
import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from app.services.broadcaster import (
    get_current_state_payload,
    realtime_manager,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Real-Time Streaming"])


@router.websocket("/ws/occupancy")
async def websocket_occupancy_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint streaming instant mess crowd & seat occupancy events.

    On connection:
    - Sends an immediate state snapshot.
    - Listens for keepalive pings from the client.
    - Pushes real-time updates when any student checks in, returns a tray, or seat times out.
    """
    await realtime_manager.connect_ws(websocket)
    try:
        # Send initial snapshot immediately upon connect
        initial_payload = get_current_state_payload("initial_snapshot")
        await websocket.send_text(json.dumps(initial_payload))

        while True:
            # Keep connection open; receive optional heartbeats or ping messages from client
            try:
                data = await websocket.receive_text()
                # Optional ping-pong response
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}))
            except WebSocketDisconnect:
                break
            except Exception:
                break
    finally:
        realtime_manager.disconnect_ws(websocket)


@router.get("/sse/occupancy", summary="Server-Sent Events Occupancy Stream")
@router.get("/sse/status", summary="Server-Sent Events Status Stream")
async def sse_occupancy_endpoint(request: Request, limit: int = None) -> StreamingResponse:
    """Server-Sent Events (SSE) streaming endpoint for real-time crowd updates.

    Ideal fallback for environments or campus firewalls that restrict WebSockets.
    """
    queue = realtime_manager.connect_sse()

    async def event_generator() -> AsyncGenerator[str, None]:
        sent = 0
        try:
            # Send initial state snapshot immediately
            initial_payload = get_current_state_payload("initial_snapshot")
            yield f"data: {json.dumps(initial_payload)}\n\n"
            sent += 1
            if limit is not None and sent >= limit:
                return

            while True:
                # Disconnect if client closed the connection
                if await request.is_disconnected():
                    break

                try:
                    # Wait for next broadcast event with 15s timeout for heartbeat
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(payload)}\n\n"
                    sent += 1
                    if limit is not None and sent >= limit:
                        return
                except asyncio.TimeoutError:
                    # Heartbeat comment to keep HTTP connection alive through firewalls/proxies
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            realtime_manager.disconnect_sse(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
