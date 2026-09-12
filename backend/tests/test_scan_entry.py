from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token, hash_password
from tests.conftest import INACTIVE_STUDENT_ID, TEST_PASSWORD, TEST_STUDENT_ID, TEST_STUDENT_NAME


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


def test_entry_scan_success_first_seat(client: TestClient) -> None:
    """Test 1: First student entering receives seat #1 and valid response structure."""
    token = _get_token(TEST_STUDENT_ID)
    response = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8842"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Entry successful"
    assert data["seatNumber"] == 1
    assert data["diningHall"] == "Central Mess"
    assert data["student"]["studentId"] == TEST_STUDENT_ID
    assert data["student"]["name"] == TEST_STUDENT_NAME
    assert "entryTime" in data
    assert "mealType" in data

    # Verify sensitive fields are not leaked
    assert "password" not in data
    assert "passwordHash" not in data
    assert "passCode" not in data

    # Verify record in MongoDB
    record = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert record is not None
    assert record["seatNumber"] == 1
    assert record["status"] == "occupied"
    assert record["exitTime"] is None
    assert record["diningHall"] == "Central Mess"


def test_entry_scan_sequential_seat_allocation(client: TestClient) -> None:
    """Test 2: Second student entering receives seat #2."""
    # First student enters -> Seat #1
    token_1 = _get_token(TEST_STUDENT_ID)
    resp_1 = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token_1}"},
        json={"passCode": "PASS-8842"},
    )
    assert resp_1.status_code == 200
    assert resp_1.json()["seatNumber"] == 1

    # Second student enters -> Seat #2
    token_2 = _get_token("STU1043")
    resp_2 = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token_2}"},
        json={"passCode": "PASS-8843"},
    )
    assert resp_2.status_code == 200
    assert resp_2.json()["seatNumber"] == 2


def test_entry_scan_lowest_available_seat_logic(client: TestClient) -> None:
    """Test 3: Lowest free virtual seat is always assigned (e.g. gaps are filled first)."""
    # Pre-occupy seat #1 and seat #3
    db_manager.occupancy.insert_many([
        {
            "studentId": "OTHER_1",
            "seatNumber": 1,
            "diningHall": "Central Mess",
            "entryTime": datetime.now(timezone.utc).isoformat(),
            "exitTime": None,
            "status": "occupied",
            "mealType": "Lunch",
        },
        {
            "studentId": "OTHER_3",
            "seatNumber": 3,
            "diningHall": "Central Mess",
            "entryTime": datetime.now(timezone.utc).isoformat(),
            "exitTime": None,
            "status": "occupied",
            "mealType": "Lunch",
        },
    ])

    # Next student enters -> should receive lowest free seat (#2)
    token = _get_token(TEST_STUDENT_ID)
    response = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8842"},
    )
    assert response.status_code == 200
    assert response.json()["seatNumber"] == 2


def test_entry_scan_duplicate_active_visit_rejected(client: TestClient) -> None:
    """Test 4: A student cannot create a second active visit while one is already occupied."""
    token = _get_token(TEST_STUDENT_ID)

    # First entry succeeds
    resp_1 = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8842"},
    )
    assert resp_1.status_code == 200

    # Second entry fails with 409 Conflict
    resp_2 = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8842"},
    )
    assert resp_2.status_code == 409
    assert "already have an active dining visit" in resp_2.json()["detail"].lower()


def test_entry_scan_mismatched_pass_code_rejected(client: TestClient) -> None:
    """Test 5: Student A cannot use Student B's passCode or an invalid passCode."""
    token = _get_token(TEST_STUDENT_ID)  # STU1042's token

    # Try entering with STU1043's passCode
    response = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8843"},
    )
    assert response.status_code == 400
    assert "invalid dining pass code" in response.json()["detail"].lower()


def test_entry_scan_inactive_student_rejected(client: TestClient) -> None:
    """Test 6: Inactive student is rejected with 403."""
    token = _get_token(INACTIVE_STUDENT_ID)
    response = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-9999"},
    )
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_entry_scan_unauthorized(client: TestClient) -> None:
    """Test 7: Missing or invalid token returns 401."""
    # No token
    resp_no_token = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8842"},
    )
    assert resp_no_token.status_code == 401

    # Invalid token
    resp_bad_token = client.post(
        "/api/scan/entry",
        headers={"Authorization": "Bearer not-a-valid-token"},
        json={"passCode": "PASS-8842"},
    )
    assert resp_bad_token.status_code == 401


def test_entry_scan_full_capacity_rejected(client: TestClient) -> None:
    """Test 8: When all 100 virtual seats are occupied, entry is rejected with 409."""
    # Occupy all 100 seats in Central Mess
    db_manager.occupancy.insert_many([
        {
            "studentId": f"FILLER_{i}",
            "seatNumber": i,
            "diningHall": "Central Mess",
            "entryTime": datetime.now(timezone.utc).isoformat(),
            "exitTime": None,
            "status": "occupied",
            "mealType": "Lunch",
        }
        for i in range(1, 101)
    ])

    token = _get_token(TEST_STUDENT_ID)
    response = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8842"},
    )
    assert response.status_code == 409
    assert "no seats are currently available" in response.json()["detail"].lower()


def test_completed_record_allows_seat_reuse(client: TestClient) -> None:
    """Test 9: Completed/expired record on seat #1 does NOT block reuse of seat #1."""
    # Insert completed record on seat #1
    db_manager.occupancy.insert_one({
        "studentId": "PAST_STUDENT",
        "seatNumber": 1,
        "diningHall": "Central Mess",
        "entryTime": datetime.now(timezone.utc).isoformat(),
        "exitTime": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
        "mealType": "Lunch",
    })

    # Student enters -> seat #1 is available and should be assigned
    token = _get_token(TEST_STUDENT_ID)
    response = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8842"},
    )
    assert response.status_code == 200
    assert response.json()["seatNumber"] == 1


def test_status_endpoint_reflects_entry(client: TestClient) -> None:
    """Test 10: GET /api/status accurately reflects the new occupancy after entry."""
    # Initially 0 occupied
    status_before = client.get("/api/status").json()
    assert status_before["occupiedSeats"] == 0
    assert status_before["availableSeats"] == 100

    # Student enters
    token = _get_token(TEST_STUDENT_ID)
    entry_resp = client.post(
        "/api/scan/entry",
        headers={"Authorization": f"Bearer {token}"},
        json={"passCode": "PASS-8842"},
    )
    assert entry_resp.status_code == 200

    # Status now reflects 1 occupied, 99 available
    status_after = client.get("/api/status").json()
    assert status_after["occupiedSeats"] == 1
    assert status_after["availableSeats"] == 99


def test_concurrent_entry_protection(client: TestClient) -> None:
    """Test 11: Concurrent entries for different students result in unique non-colliding seats."""
    # Seed 5 test students
    password_hash = hash_password(TEST_PASSWORD)
    student_records = []
    for i in range(10, 15):
        s_id = f"CONC_STU_{i}"
        p_code = f"PASS_CONC_{i}"
        db_manager.students.update_one(
            {"studentId": s_id},
            {"$set": {
                "studentId": s_id,
                "name": f"Concurrent Student {i}",
                "passCode": p_code,
                "passwordHash": password_hash,
                "isActive": True,
            }},
            upsert=True,
        )
        student_records.append((s_id, p_code))

    def attempt_entry(s_tuple):
        s_id, p_code = s_tuple
        token = _get_token(s_id)
        return client.post(
            "/api/scan/entry",
            headers={"Authorization": f"Bearer {token}"},
            json={"passCode": p_code},
        )

    # Execute entries concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        responses = list(executor.map(attempt_entry, student_records))

    assigned_seats = []
    for resp in responses:
        assert resp.status_code == 200
        assigned_seats.append(resp.json()["seatNumber"])

    # Ensure all 5 assigned seats are completely unique
    assert len(assigned_seats) == len(set(assigned_seats))
    assert set(assigned_seats) == {1, 2, 3, 4, 5}
