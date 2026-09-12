from datetime import datetime, time, timezone, timedelta
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.occupancy_service import (
    calculate_crowd_level,
    determine_current_meal_type,
)


def _seed_occupancy(count: int, status: str = "occupied") -> None:
    """Helper to insert a given number of occupancy records into mock MongoDB."""
    if count <= 0:
        return
    records = [
        {
            "studentId": f"SEED_STU_{status}_{i}_{datetime.now().timestamp()}",
            "seatNumber": i + 1,
            "diningHall": "Central Mess",
            "entryTime": datetime.now(timezone.utc),
            "exitTime": None if status == "occupied" else datetime.now(timezone.utc),
            "status": status,
            "mealType": "Lunch",
        }
        for i in range(count)
    ]
    db_manager.occupancy.insert_many(records)


def test_status_empty_collection(client: TestClient) -> None:
    """Test 1: Empty occupancy collection returns 0 occupied, 100 available, 0%, Low crowd."""
    db_manager.occupancy.delete_many({})
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["totalSeats"] == 100
    assert data["occupiedSeats"] == 0
    assert data["availableSeats"] == 100
    assert data["occupancyPercentage"] == 0
    assert data["crowdLevel"] == "Low"
    assert "updatedAt" in data
    assert "mealType" in data


def test_status_1_occupied(client: TestClient) -> None:
    """Test 2: 1 occupied seat -> 1 occupied, 99 available, 1%, Low crowd."""
    db_manager.occupancy.delete_many({})
    _seed_occupancy(1)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 1
    assert data["availableSeats"] == 99
    assert data["occupancyPercentage"] == 1
    assert data["crowdLevel"] == "Low"


def test_status_49_occupied(client: TestClient) -> None:
    """Test 3: 49 occupied seats -> 49%, Low crowd (< 50%)."""
    db_manager.occupancy.delete_many({})
    _seed_occupancy(49)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 49
    assert data["availableSeats"] == 51
    assert data["occupancyPercentage"] == 49
    assert data["crowdLevel"] == "Low"


def test_status_50_occupied(client: TestClient) -> None:
    """Test 4: 50 occupied seats -> 50%, Moderate crowd (>= 50%)."""
    db_manager.occupancy.delete_many({})
    _seed_occupancy(50)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 50
    assert data["availableSeats"] == 50
    assert data["occupancyPercentage"] == 50
    assert data["crowdLevel"] == "Moderate"


def test_status_58_occupied(client: TestClient) -> None:
    """Test 5: 58 occupied seats -> 58%, Moderate crowd, 42 available."""
    db_manager.occupancy.delete_many({})
    _seed_occupancy(58)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 58
    assert data["availableSeats"] == 42
    assert data["occupancyPercentage"] == 58
    assert data["crowdLevel"] == "Moderate"


def test_status_80_occupied(client: TestClient) -> None:
    """Test 6: 80 occupied seats -> 80%, Moderate crowd (boundary <= 80%)."""
    db_manager.occupancy.delete_many({})
    _seed_occupancy(80)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 80
    assert data["availableSeats"] == 20
    assert data["occupancyPercentage"] == 80
    assert data["crowdLevel"] == "Moderate"


def test_status_81_occupied(client: TestClient) -> None:
    """Test 7: 81 occupied seats -> 81%, Peak Rush crowd (> 80%)."""
    db_manager.occupancy.delete_many({})
    _seed_occupancy(81)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 81
    assert data["availableSeats"] == 19
    assert data["occupancyPercentage"] == 81
    assert data["crowdLevel"] == "Peak Rush"


def test_status_100_occupied(client: TestClient) -> None:
    """Test 8: 100 occupied seats -> 100%, Peak Rush, 0 available."""
    db_manager.occupancy.delete_many({})
    _seed_occupancy(100)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 100
    assert data["availableSeats"] == 0
    assert data["occupancyPercentage"] == 100
    assert data["crowdLevel"] == "Peak Rush"


def test_status_ignores_historical_and_other_records(client: TestClient) -> None:
    """Test 9 & 10: Completed, expired, or other status records are NOT counted as occupied."""
    db_manager.occupancy.delete_many({})
    # Insert 10 active
    _seed_occupancy(10, status="occupied")
    # Insert 25 completed (tray returned)
    _seed_occupancy(25, status="completed")
    # Insert 15 expired (auto-timeout)
    _seed_occupancy(15, status="expired")
    # Insert 5 cancelled
    _seed_occupancy(5, status="cancelled")

    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 10
    assert data["availableSeats"] == 90
    assert data["occupancyPercentage"] == 10
    assert data["crowdLevel"] == "Low"


def test_available_seats_never_negative(client: TestClient) -> None:
    """Test 11: Edge case where occupied seats exceed capacity doesn't produce negative available seats."""
    db_manager.occupancy.delete_many({})
    _seed_occupancy(120)  # 120 occupied when capacity is 100
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["occupiedSeats"] == 120
    assert data["availableSeats"] == 0
    assert data["occupancyPercentage"] == 100


def test_crowd_level_calculator_unit() -> None:
    """Test 12 & 13: Direct unit tests of calculate_crowd_level threshold rules."""
    assert calculate_crowd_level(0.0) == "Low"
    assert calculate_crowd_level(49.9) == "Low"
    assert calculate_crowd_level(50.0) == "Moderate"
    assert calculate_crowd_level(65.0) == "Moderate"
    assert calculate_crowd_level(80.0) == "Moderate"
    assert calculate_crowd_level(80.1) == "Peak Rush"
    assert calculate_crowd_level(100.0) == "Peak Rush"


def test_meal_type_determination_unit() -> None:
    """Test 14: Verify meal type determination during lunch, dinner, and transition hours."""
    # Test lunch hour (12:30)
    lunch_time = datetime(2026, 9, 12, 12, 30)
    assert determine_current_meal_type(lunch_time) == "Lunch"

    # Test dinner hour (19:30)
    dinner_time = datetime(2026, 9, 12, 19, 30)
    assert determine_current_meal_type(dinner_time) == "Dinner"

    # Test morning before lunch (09:00) -> upcoming Lunch
    morning_time = datetime(2026, 9, 12, 9, 0)
    assert determine_current_meal_type(morning_time) == "Lunch"

    # Test afternoon transition (16:00) -> upcoming Dinner
    afternoon_time = datetime(2026, 9, 12, 16, 0)
    assert determine_current_meal_type(afternoon_time) == "Dinner"


def test_updated_at_iso_format(client: TestClient) -> None:
    """Test 15: Verify updatedAt is a valid ISO-8601 string with timezone offset."""
    db_manager.occupancy.delete_many({})
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    updated_at_str = data["updatedAt"]
    # Parse back with datetime.fromisoformat
    parsed_dt = datetime.fromisoformat(updated_at_str)
    assert parsed_dt.tzinfo is not None
