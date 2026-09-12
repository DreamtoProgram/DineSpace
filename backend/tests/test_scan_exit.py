from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.menu_service import get_campus_timezone
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token
from tests.conftest import INACTIVE_STUDENT_ID, TEST_STUDENT_ID

OTHER_STUDENT_ID = "STU1043"


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


def test_exit_scan_success(client: TestClient) -> None:
    """Test successful exit scan: 200 OK, status='completed', exitTime populated, correct fields."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=15)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 24,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Dinner",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.post(
        "/api/scan/exit",
        json={"scanType": "tray_return"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Visit completed successfully"

    visit = data["visit"]
    assert visit["seatNumber"] == 24
    assert visit["diningHall"] == "Central Mess"
    assert visit["entryTime"] == entry_time
    assert visit["mealType"] == "Dinner"
    assert visit["durationMinutes"] == 15
    assert "exitTime" in visit
    assert visit["exitTime"] is not None

    # Check MongoDB state transition
    record = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert record is not None
    assert record["status"] == "completed"
    assert record["exitTime"] == visit["exitTime"]
    assert record["entryTime"] == entry_time
    assert record["seatNumber"] == 24


def test_exit_scan_response_fields_privacy(client: TestClient) -> None:
    """Verify that no internal IDs, passwords, passcodes, or tokens are leaked in response."""
    now = datetime.now(get_campus_timezone())
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 12,
        "diningHall": "Central Mess",
        "entryTime": now.isoformat(),
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.post(
        "/api/scan/exit",
        json={"scanType": "tray_return"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()

    assert "_id" not in data
    assert "_id" not in data["visit"]
    assert "studentId" not in data["visit"]
    assert "password" not in data
    assert "passCode" not in data


def test_exit_scan_duration_calculation(client: TestClient) -> None:
    """Verify accurate duration calculation with 18 minutes elapsed."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=18)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 5,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Breakfast",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.post(
        "/api/scan/exit",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["visit"]["durationMinutes"] == 18


def test_exit_scan_no_active_visit(client: TestClient) -> None:
    """Exit scan with no active visit returns 409 Conflict with descriptive message."""
    token = _get_token(TEST_STUDENT_ID)
    response = client.post(
        "/api/scan/exit",
        json={"scanType": "tray_return"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "No active dining visit found."


def test_exit_scan_repeated_request_rejected(client: TestClient) -> None:
    """Subsequent exit requests after visit completion must be rejected with 409 Conflict."""
    now = datetime.now(get_campus_timezone())
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 7,
        "diningHall": "Central Mess",
        "entryTime": now.isoformat(),
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    # First exit succeeds
    first_res = client.post(
        "/api/scan/exit",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first_res.status_code == 200
    first_exit_time = first_res.json()["visit"]["exitTime"]

    # Immediate second exit fails
    second_res = client.post(
        "/api/scan/exit",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_res.status_code == 409
    assert second_res.json()["detail"] == "No active dining visit found."

    # Check that database record still has original exit timestamp
    record = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert record["status"] == "completed"
    assert record["exitTime"] == first_exit_time


def test_exit_scan_completed_visit_remains_in_db(client: TestClient) -> None:
    """Verify that completed occupancy document is preserved for future history."""
    now = datetime.now(get_campus_timezone())
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 14,
        "diningHall": "Central Mess",
        "entryTime": now.isoformat(),
        "exitTime": None,
        "status": "occupied",
        "mealType": "Dinner",
    })

    token = _get_token(TEST_STUDENT_ID)
    client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})

    # Record must still exist in MongoDB
    count = db_manager.occupancy.count_documents({"studentId": TEST_STUDENT_ID})
    assert count == 1
    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc["status"] == "completed"
    assert doc["seatNumber"] == 14


def test_exit_scan_status_api_reflects_freed_seat(client: TestClient) -> None:
    """Verify that GET /api/status automatically reflects the freed seat after exit."""
    # 1. Check in student
    token = _get_token(TEST_STUDENT_ID)
    entry_res = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8842"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert entry_res.status_code == 200

    # 2. Check status: 1 occupied, 99 available
    status_before = client.get("/api/status").json()
    assert status_before["occupiedSeats"] == 1
    assert status_before["availableSeats"] == 99

    # 3. Complete visit
    exit_res = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert exit_res.status_code == 200

    # 4. Check status: 0 occupied, 100 available
    status_after = client.get("/api/status").json()
    assert status_after["occupiedSeats"] == 0
    assert status_after["availableSeats"] == 100


def test_exit_scan_seat_reuse_for_next_student(client: TestClient) -> None:
    """Verify that a freed seat is available for the next student check-in."""
    token_a = _get_token(TEST_STUDENT_ID)  # Sarah Chen, PASS-8842
    token_b = _get_token(OTHER_STUDENT_ID)  # Alex Sharma, PASS-8843

    # Student A checks in -> gets Seat 1
    entry_a = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8842"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert entry_a.status_code == 200
    assert entry_a.json()["seatNumber"] == 1

    # Student A exits -> Seat 1 is freed
    exit_a = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token_a}"})
    assert exit_a.status_code == 200

    # Student B checks in -> should receive lowest available seat, which is Seat 1
    entry_b = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8843"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert entry_b.status_code == 200
    assert entry_b.json()["seatNumber"] == 1


def test_exit_scan_student_isolation(client: TestClient) -> None:
    """Verify that Student A exiting does not affect Student B's active visit."""
    now = datetime.now(get_campus_timezone()).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 1,
        "diningHall": "Central Mess",
        "entryTime": now,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })
    db_manager.occupancy.insert_one({
        "studentId": OTHER_STUDENT_ID,
        "seatNumber": 2,
        "diningHall": "Central Mess",
        "entryTime": now,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token_a = _get_token(TEST_STUDENT_ID)
    # Student A exits
    res_a = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200

    # Student B's visit should remain active and occupied
    doc_b = db_manager.occupancy.find_one({"studentId": OTHER_STUDENT_ID})
    assert doc_b["status"] == "occupied"
    assert doc_b["exitTime"] is None
    assert doc_b["seatNumber"] == 2


def test_exit_scan_unauthorized(client: TestClient) -> None:
    """Verify that missing or invalid authorization header returns 401."""
    # Missing header
    res_missing = client.post("/api/scan/exit")
    assert res_missing.status_code == 401

    # Invalid token
    res_invalid = client.post("/api/scan/exit", headers={"Authorization": "Bearer invalid.token.xyz"})
    assert res_invalid.status_code == 401


def test_exit_scan_inactive_student(client: TestClient) -> None:
    """Verify that inactive student token returns 403 Forbidden."""
    token = _get_token(INACTIVE_STUDENT_ID)
    response = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_exit_scan_scan_type_validation(client: TestClient) -> None:
    """Verify validation of scanType field."""
    now = datetime.now(get_campus_timezone()).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 3,
        "diningHall": "Central Mess",
        "entryTime": now,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)

    # Invalid scanType
    res_invalid = client.post(
        "/api/scan/exit",
        json={"scanType": "invalid_type"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_invalid.status_code == 400
    assert "Invalid scanType" in res_invalid.json()["detail"]

    # Valid scanType
    res_valid = client.post(
        "/api/scan/exit",
        json={"scanType": "tray_return"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_valid.status_code == 200


def test_exit_scan_empty_body_and_none_body(client: TestClient) -> None:
    """Verify that both empty body {} and omitted body succeed."""
    now = datetime.now(get_campus_timezone()).isoformat()
    token = _get_token(TEST_STUDENT_ID)

    # Case 1: empty body {}
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 4,
        "diningHall": "Central Mess",
        "entryTime": now,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })
    res_empty_json = client.post(
        "/api/scan/exit",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_empty_json.status_code == 200

    # Case 2: completely omitted body
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 5,
        "diningHall": "Central Mess",
        "entryTime": now,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })
    res_no_body = client.post(
        "/api/scan/exit",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_no_body.status_code == 200


def test_exit_scan_concurrent_double_exit(client: TestClient) -> None:
    """Multi-threaded test: two simultaneous exit requests for the same student.
    Exactly one succeeds (200), the other is rejected with 409 Conflict.
    """
    now = datetime.now(get_campus_timezone()).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 8,
        "diningHall": "Central Mess",
        "entryTime": now,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)

    def do_exit():
        return client.post(
            "/api/scan/exit",
            json={"scanType": "tray_return"},
            headers={"Authorization": f"Bearer {token}"},
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(do_exit)
        f2 = executor.submit(do_exit)
        res1 = f1.result()
        res2 = f2.result()

    status_codes = sorted([res1.status_code, res2.status_code])
    assert status_codes == [200, 409], f"Expected [200, 409] but got {status_codes}"

    # Verify only 1 completed record exists
    records = list(db_manager.occupancy.find({"studentId": TEST_STUDENT_ID}))
    assert len(records) == 1
    assert records[0]["status"] == "completed"
    assert records[0]["exitTime"] is not None


def test_exit_scan_data_integrity_missing_entry_time(client: TestClient) -> None:
    """Inconsistent DB record with missing entryTime returns 500 without crashing."""
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 9,
        "diningHall": "Central Mess",
        "entryTime": None,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 500
    assert "invalid timestamp" in response.json()["detail"].lower()


def test_exit_scan_data_integrity_future_entry_time(client: TestClient) -> None:
    """Inconsistent DB record with entryTime in future returns 500 without completing visit."""
    now = datetime.now(get_campus_timezone())
    future_time = (now + timedelta(hours=2)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 10,
        "diningHall": "Central Mess",
        "entryTime": future_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    response = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 500
    assert "exit timestamp cannot precede entry" in response.json()["detail"].lower()

    # Verify record was not changed to completed
    record = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert record["status"] == "occupied"
    assert record["exitTime"] is None
