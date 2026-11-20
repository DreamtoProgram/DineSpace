import json
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token


@pytest.fixture(autouse=True)
def setup_db():
    """Clean up collections before each test."""
    db_manager.occupancy.delete_many({})
    ensure_occupancy_indexes()
    yield
    db_manager.occupancy.delete_many({})


def _get_token(student_id: str = "STU1042") -> str:
    return create_access_token(data={"sub": student_id})


def test_websocket_connect_and_receive_initial_snapshot(client: TestClient):
    """Verify WebSocket client immediately receives live initial occupancy snapshot upon connection."""
    with client.websocket_connect("/api/ws/occupancy") as ws:
        msg = ws.receive_json()
        assert msg["event"] == "occupancy_update"
        assert msg["type"] == "initial_snapshot"
        assert "occupancy" in msg
        assert msg["occupancy"]["totalSeats"] == 100
        assert "availableSeats" in msg["occupancy"]
        assert "crowdLevel" in msg["occupancy"]


def test_websocket_ping_pong(client: TestClient):
    """Verify WebSocket ping-pong keepalive message."""
    with client.websocket_connect("/api/ws/occupancy") as ws:
        # Initial snapshot
        ws.receive_json()
        # Send ping
        ws.send_text("ping")
        resp = ws.receive_json()
        assert resp["type"] == "pong"
        assert "timestamp" in resp


def test_sse_endpoint_connect(client: TestClient):
    """Verify SSE endpoint streams initial occupancy data in text/event-stream format."""
    with client.stream("GET", "/api/sse/occupancy?limit=1") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Read the first event chunk
        for line in response.iter_lines():
            if line.startswith("data: "):
                payload = json.loads(line.replace("data: ", ""))
                assert payload["event"] == "occupancy_update"
                assert payload["type"] == "initial_snapshot"
                assert payload["occupancy"]["totalSeats"] == 100
                break


def test_broadcast_triggered_on_entry_scan(client: TestClient):
    """Verify that a successful entry scan broadcasts an occupancy update to WebSocket listeners."""
    with client.websocket_connect("/api/ws/occupancy") as ws:
        # 1. Consume initial snapshot
        init_snap = ws.receive_json()
        assert init_snap["type"] == "initial_snapshot"

        # 2. Student scans entry pass
        headers = {"Authorization": f"Bearer {_get_token('STU1042')}"}
        res = client.post(
            "/api/scan/entry",
            json={"studentId": "STU1042", "passCode": "PASS-8842"},
            headers=headers,
        )
        assert res.status_code == 200
        assigned_seat = res.json()["seatNumber"]

        # 3. WebSocket listener receives real-time broadcast
        event = ws.receive_json()
        assert event["event"] == "occupancy_update"
        assert event["type"] == "checkin"
        assert event["seatNumber"] == assigned_seat
        assert event["seatStatus"] == "occupied"
        assert event["occupancy"]["totalSeats"] == 100


def test_broadcast_triggered_on_tray_return(client: TestClient):
    """Verify that a tray return checkout broadcasts real-time seat release event."""
    headers = {"Authorization": f"Bearer {_get_token('STU1042')}"}
    # 1. Check in
    enter_res = client.post(
        "/api/scan/entry",
        json={"studentId": "STU1042", "passCode": "PASS-8842"},
        headers=headers,
    )
    assert enter_res.status_code == 200
    seat_num = enter_res.json()["seatNumber"]

    with client.websocket_connect("/api/ws/occupancy") as ws:
        # Initial snapshot
        ws.receive_json()

        # Student returns tray
        exit_res = client.post(
            "/api/scan/exit",
            json={"scanType": "tray_return"},
            headers=headers,
        )
        assert exit_res.status_code == 200

        # Listener receives checkout event
        event = ws.receive_json()
        assert event["event"] == "occupancy_update"
        assert event["type"] == "checkout"
        assert event["seatNumber"] == seat_num
        assert event["seatStatus"] == "available"
