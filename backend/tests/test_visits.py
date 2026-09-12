from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.menu_service import get_campus_timezone
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token
from app.services.visit_service import calculate_visit_duration_minutes
from tests.conftest import INACTIVE_STUDENT_ID, TEST_STUDENT_ID


@pytest.fixture(autouse=True)
def setup_occupancy_collection():
    """Clean up occupancy collection and ensure indexes before each test."""
    db_manager.occupancy.delete_many({})
    ensure_occupancy_indexes()
    yield
    db_manager.occupancy.delete_many({})


def _get_token(student_id: str) -> str:
    """Helper to generate a valid access token for a student."""
    return create_access_token(data={"sub": student_id})


def test_get_current_visit_active(client: TestClient) -> None:
    """Test 1-5: Student with an active visit gets 200, active=True, and correct details."""
    now = datetime.now(get_campus_timezone())
    entry_time_8m_ago = now - timedelta(minutes=8)
    entry_iso = entry_time_8m_ago.isoformat()

    # Insert active occupancy record for TEST_STUDENT_ID
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 24,
        "diningHall": "Central Mess",
        "entryTime": entry_iso,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Dinner",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is True
    assert data["visit"] is not None
    assert data["visit"]["seatNumber"] == 24
    assert data["visit"]["diningHall"] == "Central Mess"
    assert data["visit"]["entryTime"] == entry_iso
    assert data["visit"]["mealType"] == "Dinner"
    # Duration was 8 minutes ago -> should be approximately 8 minutes
    assert data["visit"]["durationMinutes"] == 8

    # Ensure sensitive fields are not exposed
    assert "studentId" not in data["visit"]
    assert "password" not in data
    assert "passCode" not in data
    assert "_id" not in data["visit"]


def test_get_current_visit_no_active_visit(client: TestClient) -> None:
    """Test 7: Student with no active visit gets 200 with active=False and visit=None."""
    token = _get_token(TEST_STUDENT_ID)
    response = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is False
    assert data["visit"] is None


def test_get_current_visit_completed_visit_ignored(client: TestClient) -> None:
    """Test 8: Completed visit (tray returned) is NOT returned as active."""
    now_iso = datetime.now(get_campus_timezone()).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 12,
        "diningHall": "Central Mess",
        "entryTime": now_iso,
        "exitTime": now_iso,
        "status": "completed",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is False
    assert data["visit"] is None


def test_get_current_visit_expired_visit_ignored(client: TestClient) -> None:
    """Test 9: Expired visit (timed out) is NOT returned as active."""
    now_iso = datetime.now(get_campus_timezone()).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 15,
        "diningHall": "Central Mess",
        "entryTime": now_iso,
        "exitTime": now_iso,
        "status": "expired",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is False
    assert data["visit"] is None


def test_get_current_visit_isolation_between_students(client: TestClient) -> None:
    """Test 10: Student A cannot see Student B's active visit."""
    now_iso = datetime.now(get_campus_timezone()).isoformat()
    # Insert active visit for Student B (STU1043)
    db_manager.occupancy.insert_one({
        "studentId": "STU1043",
        "seatNumber": 33,
        "diningHall": "Central Mess",
        "entryTime": now_iso,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    # Student A (STU1042) queries their current visit
    token_a = _get_token(TEST_STUDENT_ID)
    response = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert response.status_code == 200
    data = response.json()
    # Student A has no active visit
    assert data["active"] is False
    assert data["visit"] is None


def test_get_current_visit_unauthorized(client: TestClient) -> None:
    """Test 11 & 12: Missing or invalid JWT returns 401."""
    # Missing token
    resp_no_token = client.get("/api/visits/current")
    assert resp_no_token.status_code == 401

    # Invalid token
    resp_bad_token = client.get(
        "/api/visits/current",
        headers={"Authorization": "Bearer bad.token.string"},
    )
    assert resp_bad_token.status_code == 401


def test_get_current_visit_inactive_student(client: TestClient) -> None:
    """Inactive student token returns 403 Forbidden."""
    token = _get_token(INACTIVE_STUDENT_ID)
    response = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_duration_calculation_unit() -> None:
    """Test 6: Direct unit test of duration calculation with controlled timestamps."""
    ref_now = datetime(2026, 9, 12, 10, 34, 0, tzinfo=timezone.utc)

    # 8 minutes earlier
    entry_8m = datetime(2026, 9, 12, 10, 26, 0, tzinfo=timezone.utc)
    assert calculate_visit_duration_minutes(entry_8m, ref_now) == 8

    # 0 seconds / same minute
    entry_0m = datetime(2026, 9, 12, 10, 34, 0, tzinfo=timezone.utc)
    assert calculate_visit_duration_minutes(entry_0m, ref_now) == 0

    # String format input
    entry_str = "2026-09-12T10:14:00+00:00"  # 20 minutes earlier
    assert calculate_visit_duration_minutes(entry_str, ref_now) == 20


def test_multiple_active_visits_edge_case(client: TestClient) -> None:
    """Test 13: Multiple active visits anomaly handled deterministically by returning most recent."""
    # Temporarily drop indexes to simulate unconstrained or legacy inconsistent data
    db_manager.occupancy.drop_indexes()

    time_old = (datetime.now(get_campus_timezone()) - timedelta(minutes=20)).isoformat()
    time_new = (datetime.now(get_campus_timezone()) - timedelta(minutes=5)).isoformat()

    # Manually insert 2 active records for same student (simulating raw anomaly bypassing API)
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 10,
        "diningHall": "Central Mess",
        "entryTime": time_old,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 15,
        "diningHall": "Central Mess",
        "entryTime": time_new,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is True
    # Most recent visit (seat 15) is returned
    assert data["visit"]["seatNumber"] == 15
    assert data["visit"]["durationMinutes"] == 5

    # Re-apply indexes for subsequent tests
    ensure_occupancy_indexes()


def test_entry_scan_then_get_current_visit_flow(client: TestClient) -> None:
    """Integration Test: POST /api/scan/entry followed by GET /api/visits/current."""
    token = _get_token(TEST_STUDENT_ID)

    # 1. Before entry: no active visit
    resp_before = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_before.status_code == 200
    assert resp_before.json()["active"] is False

    # 2. Enter dining hall
    entry_resp = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8842"},
    )
    assert entry_resp.status_code == 200
    assigned_seat = entry_resp.json()["seatNumber"]

    # 3. After entry: current visit matches assigned seat
    resp_after = client.get(
        "/api/visits/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_after.status_code == 200
    after_data = resp_after.json()
    assert after_data["active"] is True
    assert after_data["visit"]["seatNumber"] == assigned_seat
    assert after_data["visit"]["diningHall"] == "Central Mess"
    assert after_data["visit"]["durationMinutes"] == 0
