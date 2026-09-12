from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token
from app.services.timeout_service import expire_abandoned_visits
from tests.conftest import INACTIVE_STUDENT_ID, TEST_STUDENT_ID


@pytest.fixture(autouse=True)
def setup_occupancy_collection():
    """Clean up occupancy collection before each test."""
    db_manager.occupancy.delete_many({})
    ensure_occupancy_indexes()
    yield
    db_manager.occupancy.delete_many({})


def _get_token(student_id: str) -> str:
    """Generate a valid JWT bearer access token."""
    return create_access_token(data={"sub": student_id})


def _auth_header(student_id: str = TEST_STUDENT_ID) -> dict:
    """Generate the authorization headers for requests."""
    return {"Authorization": f"Bearer {_get_token(student_id)}"}


# TEST 1: Capacity = 100, No active visits -> occupiedCount = 0, availableCount = 100
def test_seats_capacity_100_no_active_visits(client: TestClient):
    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    assert data["diningHall"] == "Central Mess"
    assert data["capacity"] == 100
    assert data["occupiedCount"] == 0
    assert data["availableCount"] == 100
    assert data["mySeat"] is None
    assert data["nextAvailableSeat"] == 1
    assert len(data["seats"]) == 100
    assert all(s["status"] == "available" for s in data["seats"])


# TEST 2: Three active occupied seats -> occupiedCount = 3, availableCount = 97
def test_seats_three_active_occupied_seats(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_many([
        {"studentId": "STU1", "seatNumber": 1, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
        {"studentId": "STU2", "seatNumber": 5, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
        {"studentId": "STU3", "seatNumber": 24, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
    ])

    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedCount"] == 3
    assert data["availableCount"] == 97
    assert data["occupiedCount"] + data["availableCount"] == data["capacity"]

    # Verify individual statuses
    seat_status_map = {s["seatNumber"]: s["status"] for s in data["seats"]}
    assert seat_status_map[1] == "occupied"
    assert seat_status_map[5] == "occupied"
    assert seat_status_map[24] == "occupied"
    assert seat_status_map[2] == "available"
    assert seat_status_map[100] == "available"


# TEST 3: Completed occupancy records -> seats are available
def test_seats_completed_records_are_available(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_many([
        {"studentId": "STU1", "seatNumber": 1, "diningHall": "Central Mess", "status": "completed", "exitTime": now_iso, "entryTime": now_iso},
        {"studentId": "STU2", "seatNumber": 2, "diningHall": "Central Mess", "status": "completed", "exitTime": now_iso, "entryTime": now_iso},
    ])

    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedCount"] == 0
    assert data["availableCount"] == 100
    seat_status_map = {s["seatNumber"]: s["status"] for s in data["seats"]}
    assert seat_status_map[1] == "available"
    assert seat_status_map[2] == "available"


# TEST 4: Expired occupancy records -> seats are available
def test_seats_expired_records_are_available(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_many([
        {"studentId": "STU1", "seatNumber": 10, "diningHall": "Central Mess", "status": "expired", "exitReason": "timeout", "exitTime": now_iso, "entryTime": now_iso},
    ])

    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedCount"] == 0
    assert data["availableCount"] == 100
    seat_status_map = {s["seatNumber"]: s["status"] for s in data["seats"]}
    assert seat_status_map[10] == "available"


# TEST 5: Seat numbers are exactly 1 through capacity
def test_seats_numbers_exactly_1_through_capacity(client: TestClient):
    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    seat_numbers = [s["seatNumber"] for s in data["seats"]]
    assert seat_numbers == list(range(1, 101))


# TEST 6: No duplicate seat numbers appear in response
def test_seats_no_duplicate_seat_numbers(client: TestClient):
    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    seat_numbers = [s["seatNumber"] for s in data["seats"]]
    assert len(seat_numbers) == len(set(seat_numbers))


# TEST 7: nextAvailableSeat returns the lowest available seat
def test_seats_next_available_seat_lowest(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    # Occupy seat 1 -> nextAvailableSeat should be 2
    db_manager.occupancy.insert_one(
        {"studentId": "STU1", "seatNumber": 1, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso}
    )
    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    assert response.json()["nextAvailableSeat"] == 2

    # Now also occupy seats 2 and 3 -> next should be 4
    db_manager.occupancy.insert_many([
        {"studentId": "STU2", "seatNumber": 2, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
        {"studentId": "STU3", "seatNumber": 3, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
    ])
    response = client.get("/api/seats", headers=_auth_header())
    assert response.json()["nextAvailableSeat"] == 4

    # Now free seat 2 -> lowest available should be 2
    db_manager.occupancy.update_one({"seatNumber": 2}, {"$set": {"status": "completed", "exitTime": now_iso}})
    response = client.get("/api/seats", headers=_auth_header())
    assert response.json()["nextAvailableSeat"] == 2


# TEST 8: If all seats are occupied: occupiedCount = capacity, availableCount = 0, nextAvailableSeat = null
def test_seats_all_seats_occupied(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    all_occupied = [
        {
            "studentId": f"STU_{i}",
            "seatNumber": i,
            "diningHall": "Central Mess",
            "status": "occupied",
            "exitTime": None,
            "entryTime": now_iso,
        }
        for i in range(1, 101)
    ]
    db_manager.occupancy.insert_many(all_occupied)

    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedCount"] == 100
    assert data["availableCount"] == 0
    assert data["nextAvailableSeat"] is None
    assert all(s["status"] == "occupied" for s in data["seats"])


# TEST 9: Current authenticated student has an active visit -> mySeat contains their seat
def test_seats_my_seat_active_visit(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 42,
        "diningHall": "Central Mess",
        "status": "occupied",
        "exitTime": None,
        "entryTime": now_iso,
    })

    response = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID))
    assert response.status_code == 200
    data = response.json()
    assert data["mySeat"] == 42


# TEST 10: Current authenticated student has no active visit -> mySeat is null
def test_seats_my_seat_no_active_visit(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    # Another student occupies a seat
    db_manager.occupancy.insert_one({
        "studentId": "STU1043",
        "seatNumber": 12,
        "diningHall": "Central Mess",
        "status": "occupied",
        "exitTime": None,
        "entryTime": now_iso,
    })

    response = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID))
    assert response.status_code == 200
    data = response.json()
    assert data["mySeat"] is None


# TEST 11: Student A cannot see Student B's identity/details (privacy)
def test_seats_student_privacy_isolation(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": "STU1043",
        "seatNumber": 15,
        "diningHall": "Central Mess",
        "status": "occupied",
        "exitTime": None,
        "entryTime": now_iso,
    })

    response = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID))
    assert response.status_code == 200
    data = response.json()

    # Find seat 15 in response
    seat_15 = next(s for s in data["seats"] if s["seatNumber"] == 15)
    assert seat_15 == {"seatNumber": 15, "status": "occupied"}

    # Assert no student details are in any seat object
    for seat in data["seats"]:
        assert "studentId" not in seat
        assert "name" not in seat
        assert "passCode" not in seat
        assert "passwordHash" not in seat
        assert "mealType" not in seat
        assert "entryTime" not in seat

    # Assert response level does not expose other student's ID
    assert "STU1043" not in str(data)


# TEST 12: Unauthenticated request is rejected (401)
def test_seats_unauthenticated_rejected(client: TestClient):
    # No auth header
    response = client.get("/api/seats")
    assert response.status_code == 401

    # Invalid token
    response = client.get("/api/seats", headers={"Authorization": "Bearer invalid.token.xyz"})
    assert response.status_code == 401


# TEST 13: After tray return: occupied seat becomes available
def test_seats_after_tray_return_seat_becomes_available(client: TestClient):
    # Student enters mess
    enter_res = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8842"},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert enter_res.status_code == 200
    assigned_seat = enter_res.json()["seatNumber"]

    # Seat map reflects occupied
    map_res = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID))
    assert map_res.status_code == 200
    assert map_res.json()["occupiedCount"] == 1
    assert map_res.json()["mySeat"] == assigned_seat

    # Student performs tray return
    exit_res = client.post(
        "/api/scan/exit",
        json={"scanType": "tray_return"},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert exit_res.status_code == 200

    # Seat map immediately reflects available
    map_res_after = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID))
    assert map_res_after.status_code == 200
    assert map_res_after.json()["occupiedCount"] == 0
    assert map_res_after.json()["availableCount"] == 100
    assert map_res_after.json()["mySeat"] is None
    seat_status_map = {s["seatNumber"]: s["status"] for s in map_res_after.json()["seats"]}
    assert seat_status_map[assigned_seat] == "available"


# TEST 14: After timeout: expired seat becomes available
def test_seats_after_timeout_seat_becomes_available(client: TestClient):
    # Create visit 30 minutes ago
    entry_time = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": "STU1043",
        "seatNumber": 18,
        "diningHall": "Central Mess",
        "status": "occupied",
        "exitTime": None,
        "entryTime": entry_time,
    })

    # Initially occupied
    map_res = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID))
    assert map_res.json()["occupiedCount"] == 1

    # Sweeper runs
    expired_count = expire_abandoned_visits()
    assert expired_count == 1

    # Seat map now shows available
    map_res_after = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID))
    assert map_res_after.json()["occupiedCount"] == 0
    assert map_res_after.json()["availableCount"] == 100
    seat_status_map = {s["seatNumber"]: s["status"] for s in map_res_after.json()["seats"]}
    assert seat_status_map[18] == "available"


# TEST 15: Invalid/out-of-range occupancy record does not break the endpoint
def test_seats_out_of_range_record_handled_defensively(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_many([
        {"studentId": "STU_BAD1", "seatNumber": 101, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
        {"studentId": "STU_BAD2", "seatNumber": -5, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
        {"studentId": "STU_BAD3", "seatNumber": "not_an_int", "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
        {"studentId": "STU_GOOD", "seatNumber": 50, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
    ])

    response = client.get("/api/seats", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    assert data["capacity"] == 100
    # Only seat 50 is a valid occupied seat
    assert data["occupiedCount"] == 1
    assert data["availableCount"] == 99
    assert len(data["seats"]) == 100
    seat_numbers = [s["seatNumber"] for s in data["seats"]]
    assert seat_numbers == list(range(1, 101))
    assert 101 not in seat_numbers


# TEST 16: Endpoint does not return sensitive credentials
def test_seats_no_sensitive_credentials_in_response(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 1,
        "diningHall": "Central Mess",
        "status": "occupied",
        "exitTime": None,
        "entryTime": now_iso,
        "passCode": "SECRET_PASS",
        "passwordHash": "$2b$12$secretpasswordhash",
    })

    response = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID))
    assert response.status_code == 200
    text = response.text
    assert "SECRET_PASS" not in text
    assert "$2b$12$" not in text
    assert "passwordHash" not in text
    assert "passCode" not in text


# TEST 17: MongoDB is queried in bulk rather than once per seat
def test_seats_bulk_query_single_mongo_call(client: TestClient):
    with patch.object(db_manager.occupancy, "find", wraps=db_manager.occupancy.find) as mock_find:
        response = client.get("/api/seats", headers=_auth_header())
        assert response.status_code == 200
        # Exactly 1 bulk query to find occupied seats, NOT 100 queries in a loop!
        assert mock_find.call_count == 1


# TEST 18: Query parameter status filtering
def test_seats_status_filtering(client: TestClient):
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_many([
        {"studentId": "STU1", "seatNumber": 2, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
        {"studentId": "STU2", "seatNumber": 4, "diningHall": "Central Mess", "status": "occupied", "exitTime": None, "entryTime": now_iso},
    ])

    # Filter by available
    res_avail = client.get("/api/seats?status=available", headers=_auth_header())
    assert res_avail.status_code == 200
    data_avail = res_avail.json()
    assert data_avail["occupiedCount"] == 2
    assert data_avail["availableCount"] == 98
    assert len(data_avail["seats"]) == 98
    assert all(s["status"] == "available" for s in data_avail["seats"])
    avail_numbers = [s["seatNumber"] for s in data_avail["seats"]]
    assert 2 not in avail_numbers
    assert 4 not in avail_numbers

    # Filter by occupied
    res_occ = client.get("/api/seats?status=occupied", headers=_auth_header())
    assert res_occ.status_code == 200
    data_occ = res_occ.json()
    assert data_occ["occupiedCount"] == 2
    assert data_occ["availableCount"] == 98
    assert len(data_occ["seats"]) == 2
    assert all(s["status"] == "occupied" for s in data_occ["seats"])
    occ_numbers = [s["seatNumber"] for s in data_occ["seats"]]
    assert occ_numbers == [2, 4]

    # Invalid status filter -> 422
    res_bad = client.get("/api/seats?status=reserved", headers=_auth_header())
    assert res_bad.status_code == 422


# TEST 19: Inactive student account is rejected (403)
def test_seats_inactive_student_rejected(client: TestClient):
    response = client.get("/api/seats", headers=_auth_header(INACTIVE_STUDENT_ID))
    assert response.status_code == 403


# TEST 20: Consistency between /api/status, /api/seats, and /api/visits/current
def test_seats_consistency_with_status_and_visits(client: TestClient):
    # Empty
    status_data = client.get("/api/status").json()
    seats_data = client.get("/api/seats", headers=_auth_header()).json()
    assert status_data["occupiedSeats"] == seats_data["occupiedCount"]
    assert status_data["availableSeats"] == seats_data["availableCount"]

    # Student enters
    client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8842"},
        headers=_auth_header(TEST_STUDENT_ID),
    )

    status_data_after = client.get("/api/status").json()
    seats_data_after = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID)).json()
    visit_data = client.get("/api/visits/current", headers=_auth_header(TEST_STUDENT_ID)).json()

    assert status_data_after["occupiedSeats"] == 1
    assert seats_data_after["occupiedCount"] == 1
    assert status_data_after["occupiedSeats"] == seats_data_after["occupiedCount"]
    assert seats_data_after["mySeat"] == visit_data["visit"]["seatNumber"]
