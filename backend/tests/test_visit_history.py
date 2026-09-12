from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.menu_service import get_campus_timezone
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token
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


def test_history_completed_visits(client: TestClient):
    """TEST 1: Authenticated student with completed visits receives them."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=45)).isoformat()
    exit_time = (now - timedelta(minutes=25)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 12,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": exit_time,
        "status": "completed",
        "exitReason": "tray_return",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["visits"]) == 1
    assert data["visits"][0]["seatNumber"] == 12
    assert data["visits"][0]["status"] == "completed"
    assert data["visits"][0]["exitReason"] == "tray_return"
    assert data["pagination"]["total"] == 1


def test_history_expired_visits(client: TestClient):
    """TEST 2: Authenticated student with expired visits receives them."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=60)).isoformat()
    exit_time = (now - timedelta(minutes=35)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 18,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": exit_time,
        "status": "expired",
        "exitReason": "timeout",
        "mealType": "Dinner",
    })

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["visits"]) == 1
    assert data["visits"][0]["seatNumber"] == 18
    assert data["visits"][0]["status"] == "expired"
    assert data["visits"][0]["exitReason"] == "timeout"


def test_history_both_completed_and_expired(client: TestClient):
    """TEST 3: Authenticated student with both completed and expired visits receives both."""
    now = datetime.now(get_campus_timezone())

    db_manager.occupancy.insert_many([
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 20,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=3)).isoformat(),
            "exitTime": (now - timedelta(hours=2, minutes=40)).isoformat(),
            "status": "completed",
            "exitReason": "tray_return",
            "mealType": "Lunch",
        },
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 22,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=1)).isoformat(),
            "exitTime": (now - timedelta(minutes=35)).isoformat(),
            "status": "expired",
            "exitReason": "timeout",
            "mealType": "Dinner",
        },
    ])

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["visits"]) == 2
    assert data["pagination"]["total"] == 2
    statuses = {v["status"] for v in data["visits"]}
    assert statuses == {"completed", "expired"}


def test_history_active_visit_excluded(client: TestClient):
    """TEST 4: Active occupied visit is strictly excluded from visit history."""
    now = datetime.now(get_campus_timezone())

    # 1 completed, 1 active
    db_manager.occupancy.insert_many([
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 5,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=2)).isoformat(),
            "exitTime": (now - timedelta(hours=1, minutes=40)).isoformat(),
            "status": "completed",
            "exitReason": "tray_return",
            "mealType": "Lunch",
        },
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 6,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(minutes=10)).isoformat(),
            "exitTime": None,
            "status": "occupied",
            "mealType": "Dinner",
        },
    ])

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["visits"]) == 1
    assert data["visits"][0]["seatNumber"] == 5
    assert data["pagination"]["total"] == 1


def test_history_empty_returns_200_empty_list(client: TestClient):
    """TEST 5: Student with no past visits receives 200 OK with empty array and total 0."""
    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["visits"] == []
    assert data["pagination"]["total"] == 0
    assert data["pagination"]["limit"] == 20
    assert data["pagination"]["offset"] == 0


def test_history_sorted_newest_first_by_exit_time(client: TestClient):
    """TEST 6: History is sorted newest first using exitTime descending."""
    now = datetime.now(get_campus_timezone())

    older_exit = (now - timedelta(hours=2)).isoformat()
    newer_exit = (now - timedelta(minutes=30)).isoformat()

    # Insert older visit first, then newer
    db_manager.occupancy.insert_many([
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 1,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=2, minutes=20)).isoformat(),
            "exitTime": older_exit,
            "status": "completed",
            "mealType": "Lunch",
        },
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 2,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(minutes=50)).isoformat(),
            "exitTime": newer_exit,
            "status": "completed",
            "mealType": "Dinner",
        },
    ])

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    visits = res.json()["visits"]
    assert len(visits) == 2
    # First item must be newer_exit (Seat 2)
    assert visits[0]["seatNumber"] == 2
    assert visits[0]["exitTime"] == newer_exit
    # Second item must be older_exit (Seat 1)
    assert visits[1]["seatNumber"] == 1
    assert visits[1]["exitTime"] == older_exit


def test_history_duration_calculated_correctly(client: TestClient):
    """TEST 7: durationMinutes is computed on the fly from exitTime - entryTime."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=35)).isoformat()
    exit_time = (now - timedelta(minutes=13)).isoformat()  # 22 minutes duration

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 33,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": exit_time,
        "status": "completed",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    visit = res.json()["visits"][0]
    assert visit["durationMinutes"] == 22


def test_history_student_isolation(client: TestClient):
    """TEST 8: Student A cannot see Student B's visit history."""
    now = datetime.now(get_campus_timezone())

    # Insert visit for Student A and visit for Student B
    db_manager.occupancy.insert_many([
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 10,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=1)).isoformat(),
            "exitTime": (now - timedelta(minutes=40)).isoformat(),
            "status": "completed",
            "mealType": "Lunch",
        },
        {
            "studentId": OTHER_STUDENT_ID,
            "seatNumber": 11,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=1)).isoformat(),
            "exitTime": (now - timedelta(minutes=40)).isoformat(),
            "status": "completed",
            "mealType": "Lunch",
        },
    ])

    token_a = _get_token(TEST_STUDENT_ID)
    res_a = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    visits_a = res_a.json()["visits"]
    assert len(visits_a) == 1
    assert visits_a[0]["seatNumber"] == 10

    # Ensure Student A cannot query Student B via query param
    res_spoof = client.get(
        f"/api/visits/history?studentId={OTHER_STUDENT_ID}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    # Even if query param is passed, it is ignored and only Student A's visits are returned
    assert res_spoof.status_code == 200
    assert len(res_spoof.json()["visits"]) == 1
    assert res_spoof.json()["visits"][0]["seatNumber"] == 10


def test_history_unauthenticated_rejected(client: TestClient):
    """TEST 9: Request without token or with invalid token is rejected with 401."""
    # Missing token
    res_missing = client.get("/api/visits/history")
    assert res_missing.status_code == 401

    # Invalid token
    res_invalid = client.get(
        "/api/visits/history",
        headers={"Authorization": "Bearer bad.token.here"},
    )
    assert res_invalid.status_code == 401


def test_history_pagination_limit(client: TestClient):
    """TEST 10: limit parameter restricts number of returned items."""
    now = datetime.now(get_campus_timezone())

    # Insert 5 visits
    for i in range(5):
        db_manager.occupancy.insert_one({
            "studentId": TEST_STUDENT_ID,
            "seatNumber": i + 1,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=5 - i)).isoformat(),
            "exitTime": (now - timedelta(hours=5 - i, minutes=-20)).isoformat(),
            "status": "completed",
            "mealType": "Lunch",
        })

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history?limit=2", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["visits"]) == 2
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["total"] == 5


def test_history_pagination_offset(client: TestClient):
    """TEST 11: offset parameter skips items."""
    now = datetime.now(get_campus_timezone())

    # Insert 3 visits with increasing exit times
    for i in range(3):
        db_manager.occupancy.insert_one({
            "studentId": TEST_STUDENT_ID,
            "seatNumber": i + 1,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=3 - i)).isoformat(),
            "exitTime": (now - timedelta(hours=3 - i, minutes=-20)).isoformat(),
            "status": "completed",
            "mealType": "Lunch",
        })

    token = _get_token(TEST_STUDENT_ID)
    # With limit=1, offset=1: gets the second newest visit (seat 2)
    res = client.get(
        "/api/visits/history?limit=1&offset=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["visits"]) == 1
    assert data["visits"][0]["seatNumber"] == 2
    assert data["pagination"]["offset"] == 1
    assert data["pagination"]["total"] == 3


def test_history_invalid_limit_rejected(client: TestClient):
    """TEST 12: limit <= 0 returns 422 Unprocessable Entity."""
    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history?limit=0", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422


def test_history_negative_offset_rejected(client: TestClient):
    """TEST 13: offset < 0 returns 422 Unprocessable Entity."""
    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history?offset=-1", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422


def test_history_limit_above_max_rejected(client: TestClient):
    """TEST 14: limit > 100 returns 422 Unprocessable Entity."""
    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history?limit=101", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422


def test_history_no_internal_id_leaked(client: TestClient):
    """TEST 15: Response does not expose MongoDB _id, passwordHash, or passCode."""
    now = datetime.now(get_campus_timezone())
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 16,
        "diningHall": "Central Mess",
        "entryTime": (now - timedelta(hours=1)).isoformat(),
        "exitTime": (now - timedelta(minutes=40)).isoformat(),
        "status": "completed",
        "exitReason": "tray_return",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    visit = data["visits"][0]

    assert "_id" not in visit
    assert "_id" not in data
    assert "passwordHash" not in visit
    assert "password" not in visit
    assert "passCode" not in visit


def test_history_expired_status_retained(client: TestClient):
    """TEST 16: Expired visit retains status='expired'."""
    now = datetime.now(get_campus_timezone())
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 50,
        "diningHall": "Central Mess",
        "entryTime": (now - timedelta(hours=1)).isoformat(),
        "exitTime": (now - timedelta(minutes=35)).isoformat(),
        "status": "expired",
        "exitReason": "timeout",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    visit = res.json()["visits"][0]
    assert visit["status"] == "expired"


def test_history_completed_status_retained(client: TestClient):
    """TEST 17: Completed tray-return visit retains status='completed'."""
    now = datetime.now(get_campus_timezone())
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 51,
        "diningHall": "Central Mess",
        "entryTime": (now - timedelta(hours=1)).isoformat(),
        "exitTime": (now - timedelta(minutes=40)).isoformat(),
        "status": "completed",
        "exitReason": "tray_return",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    visit = res.json()["visits"][0]
    assert visit["status"] == "completed"


def test_history_exit_reason_returned(client: TestClient):
    """TEST 18: exitReason is correctly returned for both tray_return and timeout."""
    now = datetime.now(get_campus_timezone())
    db_manager.occupancy.insert_many([
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 1,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=2)).isoformat(),
            "exitTime": (now - timedelta(hours=1, minutes=40)).isoformat(),
            "status": "completed",
            "exitReason": "tray_return",
            "mealType": "Lunch",
        },
        {
            "studentId": TEST_STUDENT_ID,
            "seatNumber": 2,
            "diningHall": "Central Mess",
            "entryTime": (now - timedelta(hours=1)).isoformat(),
            "exitTime": (now - timedelta(minutes=35)).isoformat(),
            "status": "expired",
            "exitReason": "timeout",
            "mealType": "Dinner",
        },
    ])

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/visits/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    reasons = {v["exitReason"] for v in res.json()["visits"]}
    assert reasons == {"tray_return", "timeout"}
