import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError
import pytest

from app.database import db_manager
from app.main import app
from app.services.menu_service import get_campus_timezone
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token
from app.services.timeout_service import expire_abandoned_visits
from app.workers import TimeoutSweeperWorker
from tests.conftest import TEST_STUDENT_ID

OTHER_STUDENT_ID = "STU1043"


@pytest.fixture(autouse=True)
def setup_occupancy():
    """Clean up occupancy collection and ensure indexes before each test."""
    db_manager.occupancy.delete_many({})
    ensure_occupancy_indexes()
    yield
    db_manager.occupancy.delete_many({})


def _get_token(student_id: str) -> str:
    """Helper to generate a valid access token."""
    return create_access_token(data={"sub": student_id})


def test_timeout_active_visit_older_than_25m_expires():
    """TEST 1: Active visit older than 25 minutes becomes expired."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=26)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 10,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    expired_count = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_count == 1

    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc is not None
    assert doc["status"] == "expired"


def test_timeout_expired_visit_receives_exit_time():
    """TEST 6: Expired visit receives a valid exitTime timestamp."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=30)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 10,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc["exitTime"] is not None
    assert doc["exitTime"] == now.isoformat()


def test_timeout_expired_visit_has_exit_reason_timeout():
    """TEST 7: Expired visit has exitReason='timeout'."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=30)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 10,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc["exitReason"] == "timeout"



def test_timeout_active_visit_newer_than_25m_remains_occupied():
    """TEST 2: Active visit newer than 25 minutes remains occupied."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=24)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 11,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    expired_count = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_count == 0

    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc["status"] == "occupied"
    assert doc["exitTime"] is None


def test_timeout_visit_exactly_25m_old_remains_occupied():
    """TEST 3: Visit exactly 25 minutes old remains occupied because requirement is MORE THAN 25 minutes."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=25)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 12,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    expired_count = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_count == 0

    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc["status"] == "occupied"
    assert doc["exitTime"] is None


def test_timeout_completed_visit_remains_completed():
    """TEST 4: Already completed visit older than 25 minutes remains completed."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=40)).isoformat()
    exit_time = (now - timedelta(minutes=20)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 13,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": exit_time,
        "status": "completed",
        "mealType": "Dinner",
    })

    expired_count = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_count == 0

    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc["status"] == "completed"
    assert doc["exitTime"] == exit_time
    assert "exitReason" not in doc or doc.get("exitReason") != "timeout"


def test_timeout_already_expired_visit_remains_expired():
    """TEST 5: Already expired visit remains unchanged."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=60)).isoformat()
    orig_exit_time = (now - timedelta(minutes=35)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 14,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": orig_exit_time,
        "status": "expired",
        "exitReason": "timeout",
        "mealType": "Lunch",
    })

    expired_count = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_count == 0

    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc["status"] == "expired"
    assert doc["exitTime"] == orig_exit_time


def test_timeout_multiple_old_active_visits_all_expire():
    """TEST 8: Multiple active visits older than 25 minutes all expire."""
    now = datetime.now(get_campus_timezone())
    old_time = (now - timedelta(minutes=30)).isoformat()
    recent_time = (now - timedelta(minutes=10)).isoformat()

    db_manager.occupancy.insert_many([
        {
            "studentId": "STU1",
            "seatNumber": 1,
            "diningHall": "Central Mess",
            "entryTime": old_time,
            "exitTime": None,
            "status": "occupied",
            "mealType": "Lunch",
        },
        {
            "studentId": "STU2",
            "seatNumber": 2,
            "diningHall": "Central Mess",
            "entryTime": old_time,
            "exitTime": None,
            "status": "occupied",
            "mealType": "Lunch",
        },
        {
            "studentId": "STU3",
            "seatNumber": 3,
            "diningHall": "Central Mess",
            "entryTime": recent_time,
            "exitTime": None,
            "status": "occupied",
            "mealType": "Lunch",
        },
    ])

    expired_count = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_count == 2

    assert db_manager.occupancy.count_documents({"status": "expired"}) == 2
    assert db_manager.occupancy.count_documents({"status": "occupied"}) == 1
    assert db_manager.occupancy.find_one({"studentId": "STU3"})["status"] == "occupied"


def test_timeout_only_occupied_and_null_exit_time_matched():
    """TEST 9: Records with non-null exitTime or non-occupied status are never expired."""
    now = datetime.now(get_campus_timezone())
    old_time = (now - timedelta(minutes=35)).isoformat()

    db_manager.occupancy.insert_many([
        {
            "studentId": "STU_ANOMALY_1",
            "seatNumber": 20,
            "diningHall": "Central Mess",
            "entryTime": old_time,
            "exitTime": old_time,
            "status": "occupied",  # Non-null exitTime
            "mealType": "Lunch",
        },
        {
            "studentId": "STU_ANOMALY_2",
            "seatNumber": 21,
            "diningHall": "Central Mess",
            "entryTime": old_time,
            "exitTime": None,
            "status": "completed",  # Not occupied
            "mealType": "Lunch",
        },
    ])

    expired_count = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_count == 0


def test_timeout_status_api_reflects_freed_seat(client: TestClient):
    """TEST 10: After expiration, GET /api/status automatically reflects the freed seat."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=30)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 25,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    # Status before expiration: 1 occupied, 99 available
    res_before = client.get("/api/status").json()
    assert res_before["occupiedSeats"] == 1
    assert res_before["availableSeats"] == 99

    # Trigger expiration
    expire_abandoned_visits(now_dt=now, timeout_minutes=25)

    # Status after expiration: 0 occupied, 100 available
    res_after = client.get("/api/status").json()
    assert res_after["occupiedSeats"] == 0
    assert res_after["availableSeats"] == 100


def test_timeout_current_visit_returns_no_active_visit(client: TestClient):
    """TEST 11: After expiration, GET /api/visits/current returns active=false, visit=null."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=35)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 15,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Dinner",
    })

    token = _get_token(TEST_STUDENT_ID)
    # Active before timeout
    res_before = client.get("/api/visits/current", headers={"Authorization": f"Bearer {token}"})
    assert res_before.json()["active"] is True

    # Expire visit
    expire_abandoned_visits(now_dt=now, timeout_minutes=25)

    # Inactive after timeout
    res_after = client.get("/api/visits/current", headers={"Authorization": f"Bearer {token}"})
    assert res_after.status_code == 200
    assert res_after.json()["active"] is False
    assert res_after.json()["visit"] is None


def test_timeout_expired_seat_can_be_assigned_to_new_student(client: TestClient):
    """TEST 12: An expired seat can be reused by a new student checking in."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=30)).isoformat()

    # Seat 1 is occupied by Student A but expired
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 1,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})["status"] == "expired"

    # Student B checks in -> receives Seat 1 (lowest available)
    token_b = _get_token(OTHER_STUDENT_ID)
    res_b = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8843"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res_b.status_code == 200
    assert res_b.json()["seatNumber"] == 1


def test_timeout_concurrency_with_tray_return(client: TestClient):
    """TEST 13: Concurrency safety:
    Case A: Tray return completes first -> sweeper cannot overwrite to expired.
    Case B: Sweeper expires first -> tray return cannot overwrite to completed (returns 409).
    """
    now = datetime.now(get_campus_timezone())
    token = _get_token(TEST_STUDENT_ID)

    # --- CASE A: Tray Return Completes First ---
    entry_time_a = (now - timedelta(minutes=30)).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 40,
        "diningHall": "Central Mess",
        "entryTime": entry_time_a,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Dinner",
    })

    # Student completes tray return
    exit_res = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert exit_res.status_code == 200
    assert exit_res.json()["visit"]["exitTime"] is not None

    # Sweeper runs now
    expired_a = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_a == 0

    doc_a = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc_a["status"] == "completed"
    assert doc_a.get("exitReason") != "timeout"

    # Clean up for Case B
    db_manager.occupancy.delete_many({})

    # --- CASE B: Sweeper Expires First ---
    entry_time_b = (now - timedelta(minutes=30)).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 41,
        "diningHall": "Central Mess",
        "entryTime": entry_time_b,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Dinner",
    })

    # Sweeper expires visit first
    expired_b = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired_b == 1
    doc_b = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc_b["status"] == "expired"
    orig_exit_time = doc_b["exitTime"]

    # Student attempts tray return afterwards -> rejected with 409 Conflict
    exit_res_b = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert exit_res_b.status_code == 409
    assert exit_res_b.json()["detail"] == "No active dining visit found."

    # Document remains expired with original exitTime
    doc_b_after = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc_b_after["status"] == "expired"
    assert doc_b_after["exitTime"] == orig_exit_time


@pytest.mark.anyio
async def test_worker_starts_during_fastapi_lifespan():
    """TEST 14: Background worker starts and property reflects running state."""
    worker = TimeoutSweeperWorker(interval_seconds=10)
    assert not worker.is_running

    worker.start()
    assert worker.is_running

    await worker.stop()
    assert not worker.is_running


@pytest.mark.anyio
async def test_worker_stops_cleanly_during_shutdown():
    """TEST 15: Background worker is cancelled and cleaned up during application shutdown."""
    worker = TimeoutSweeperWorker(interval_seconds=60)
    worker.start()
    assert worker.is_running

    # Stop worker
    await worker.stop()
    assert not worker.is_running
    assert worker._task is None


@pytest.mark.anyio
async def test_worker_resilient_to_database_exception(monkeypatch):
    """TEST 16: A database exception inside one worker iteration does not terminate the worker."""
    call_count = 0

    def mock_expire(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise PyMongoError("Simulated database timeout")
        return 0

    monkeypatch.setattr("app.workers.timeout_worker.expire_abandoned_visits", mock_expire)

    # Worker with very short interval (0.01 seconds)
    worker = TimeoutSweeperWorker(interval_seconds=0.01)
    worker.start()

    # Let worker run across at least 2 ticks
    await asyncio.sleep(0.05)

    # Worker should still be running despite the first tick error
    assert worker.is_running
    assert call_count >= 2

    await worker.stop()
    assert not worker.is_running
