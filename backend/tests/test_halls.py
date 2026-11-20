import json
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager


def test_list_dining_halls(client: TestClient) -> None:
    """Test 1: GET /api/halls returns all 3 campus dining halls with full metadata and live status."""
    response = client.get("/api/halls")
    assert response.status_code == 200
    data = response.json()

    assert data["totalHalls"] == 3
    assert data["defaultHall"] == "Central Mess"
    assert len(data["halls"]) == 3

    hall_names = [h["name"] for h in data["halls"]]
    assert "Central Mess" in hall_names
    assert "North Hostel Mess" in hall_names
    assert "Food Court (Student Center)" in hall_names

    # Check that status is embedded
    central = next(h for h in data["halls"] if h["name"] == "Central Mess")
    assert central["capacity"] == 100
    assert central["campus"] == "Main Campus"
    assert "status" in central
    assert central["status"]["totalSeats"] == 100
    assert central["status"]["diningHall"] == "Central Mess"

    north = next(h for h in data["halls"] if h["name"] == "North Hostel Mess")
    assert north["capacity"] == 80
    assert north["status"]["totalSeats"] == 80

    food_court = next(h for h in data["halls"] if h["name"] == "Food Court (Student Center)")
    assert food_court["capacity"] == 120
    assert food_court["status"]["totalSeats"] == 120


def test_get_single_dining_hall(client: TestClient) -> None:
    """Test 2: GET /api/halls/{hall_id} returns details for a specific hall."""
    res = client.get("/api/halls/central-mess")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Central Mess"
    assert data["capacity"] == 100

    res2 = client.get("/api/halls/north-hostel-mess")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["name"] == "North Hostel Mess"
    assert data2["capacity"] == 80

    # Non-existent hall returns 404
    res_err = client.get("/api/halls/nonexistent-hall-999")
    assert res_err.status_code == 404


def test_status_endpoint_with_dining_hall(client: TestClient) -> None:
    """Test 3: GET /api/status?diningHall=... returns capacity and metrics tailored to the hall."""
    res_default = client.get("/api/status")
    assert res_default.status_code == 200
    assert res_default.json()["totalSeats"] == 100
    assert res_default.json()["diningHall"] == "Central Mess"

    res_north = client.get("/api/status?diningHall=North+Hostel+Mess")
    assert res_north.status_code == 200
    data_north = res_north.json()
    assert data_north["totalSeats"] == 80
    assert data_north["diningHall"] == "North Hostel Mess"

    res_fc = client.get("/api/status?diningHall=Food+Court+(Student+Center)")
    assert res_fc.status_code == 200
    data_fc = res_fc.json()
    assert data_fc["totalSeats"] == 120
    assert data_fc["diningHall"] == "Food Court (Student Center)"


def test_seats_map_with_dining_hall(client: TestClient) -> None:
    """Test 4: GET /api/seats?diningHall=... returns accurate capacity for the target hall."""
    from app.services.security import create_access_token
    token = create_access_token(data={"sub": "STU1042"})
    headers = {"Authorization": f"Bearer {token}"}

    res_central = client.get("/api/seats?diningHall=Central+Mess", headers=headers)
    assert res_central.status_code == 200
    assert res_central.json()["capacity"] == 100
    assert res_central.json()["diningHall"] == "Central Mess"

    res_north = client.get("/api/seats?diningHall=North+Hostel+Mess", headers=headers)
    assert res_north.status_code == 200
    assert res_north.json()["capacity"] == 80
    assert res_north.json()["diningHall"] == "North Hostel Mess"

    res_fc = client.get("/api/seats?diningHall=Food+Court+(Student+Center)", headers=headers)
    assert res_fc.status_code == 200
    assert res_fc.json()["capacity"] == 120
    assert res_fc.json()["diningHall"] == "Food Court (Student Center)"


def test_today_menu_with_dining_hall(client: TestClient) -> None:
    """Test 5: GET /api/menu/today?diningHall=... returns menu filtered or specialized for that facility."""
    res_central = client.get("/api/menu/today?diningHall=Central+Mess")
    assert res_central.status_code == 200
    menus = res_central.json()["menus"]
    assert len(menus) >= 1

    res_north = client.get("/api/menu/today?diningHall=North+Hostel+Mess")
    assert res_north.status_code == 200
    menus_north = res_north.json()["menus"]
    assert len(menus_north) >= 1
    # Verify North Hostel dishes are present in lunch menu
    lunch_north = next((m for m in menus_north if m["mealType"] == "Lunch"), None)
    if lunch_north:
        dish_names = [item["name"] for item in lunch_north["items"]]
        assert "Amritsari Chole Kulche" in dish_names


def test_realtime_sse_with_dining_hall(client: TestClient) -> None:
    """Test 6: GET /api/sse/occupancy?diningHall=North+Hostel+Mess&limit=1 returns snapshot for North Hostel."""
    with client.stream("GET", "/api/sse/occupancy?diningHall=North+Hostel+Mess&limit=1") as response:
        assert response.status_code == 200
        for line in response.iter_lines():
            if line.startswith("data: "):
                payload = json.loads(line[6:])
                assert payload["event"] == "occupancy_update"
                assert payload["diningHall"] == "North Hostel Mess"
                assert payload["occupancy"]["totalSeats"] == 80
                break
