from datetime import datetime, timezone
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


def _get_admin_token() -> str:
    """Generate JWT token for Admin user."""
    return create_access_token(data={"sub": "ADMIN01"})


def _get_student_token() -> str:
    """Generate JWT token for regular Student."""
    return create_access_token(data={"sub": "STU1042"})


def test_admin_login_success(client: TestClient):
    """Verify admin login returns JWT and admin profile with role='admin'."""
    res = client.post(
        "/api/auth/login",
        json={"studentId": "ADMIN01", "password": "DineSpace2026!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "accessToken" in data
    assert data["student"]["studentId"] == "ADMIN01"
    assert data["student"]["role"] == "admin"
    assert "Manager" in data["student"]["name"]


def test_admin_endpoints_require_admin_role(client: TestClient):
    """Verify regular student accounts receive 403 Forbidden on admin endpoints."""
    student_headers = {"Authorization": f"Bearer {_get_student_token()}"}

    # 1. Analytics
    res1 = client.get("/api/admin/analytics", headers=student_headers)
    assert res1.status_code == 403

    # 2. Admin seats
    res2 = client.get("/api/admin/seats", headers=student_headers)
    assert res2.status_code == 403

    # 3. Update seat
    res3 = client.post(
        "/api/admin/seats/status",
        json={"seatNumber": 12, "status": "maintenance"},
        headers=student_headers,
    )
    assert res3.status_code == 403

    # 4. Release seat
    res4 = client.post(
        "/api/admin/seats/release",
        json={"seatNumber": 24},
        headers=student_headers,
    )
    assert res4.status_code == 403


def test_admin_get_analytics(client: TestClient):
    """Verify admin can retrieve operational analytics."""
    admin_headers = {"Authorization": f"Bearer {_get_admin_token()}"}
    res = client.get("/api/admin/analytics", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["diningHall"] == "Central Mess"
    assert data["capacity"] == 100
    assert "occupancyRate" in data
    assert "totalServedToday" in data
    assert "avgDiningDurationMinutes" in data
    assert "seatTurnoverRate" in data
    assert len(data["hourlyThroughput"]) > 0


def test_admin_get_seats(client: TestClient):
    """Verify admin can list all 100 seats."""
    admin_headers = {"Authorization": f"Bearer {_get_admin_token()}"}
    res = client.get("/api/admin/seats", headers=admin_headers)
    assert res.status_code == 200
    seats = res.json()
    assert len(seats) == 100
    assert seats[0]["seatNumber"] == 1
    assert "status" in seats[0]


def test_admin_set_seat_status_maintenance_and_available(client: TestClient):
    """Verify admin can mark a seat as maintenance and later reset it to available."""
    admin_headers = {"Authorization": f"Bearer {_get_admin_token()}"}

    # Mark seat 15 as maintenance
    res = client.post(
        "/api/admin/seats/status",
        json={"seatNumber": 15, "status": "maintenance", "note": "Broken chair"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "maintenance"

    # Verify student seat map sees seat 15 as maintenance
    student_headers = {"Authorization": f"Bearer {_get_student_token()}"}
    seats_res = client.get("/api/seats", headers=student_headers)
    assert seats_res.status_code == 200
    seat_15 = next(s for s in seats_res.json()["seats"] if s["seatNumber"] == 15)
    assert seat_15["status"] == "maintenance"

    # Verify admin seats endpoint sees note
    admin_seats = client.get("/api/admin/seats", headers=admin_headers)
    assert admin_seats.status_code == 200
    admin_seat_15 = next(s for s in admin_seats.json() if s["seatNumber"] == 15)
    assert admin_seat_15["status"] == "maintenance"
    assert admin_seat_15["note"] == "Broken chair"

    # Reset seat 15 to available
    reset_res = client.post(
        "/api/admin/seats/status",
        json={"seatNumber": 15, "status": "available"},
        headers=admin_headers,
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "available"

    # Verify student seat map sees seat 15 as available again
    seats_res2 = client.get("/api/seats", headers=student_headers)
    seat_15_after = next(s for s in seats_res2.json()["seats"] if s["seatNumber"] == 15)
    assert seat_15_after["status"] == "available"


def test_admin_force_release_seat(client: TestClient):
    """Verify admin can force-release an occupied seat."""
    admin_headers = {"Authorization": f"Bearer {_get_admin_token()}"}

    # Simulate an active occupied seat 24
    now_iso = datetime.now(timezone.utc).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": "STU1042",
        "seatNumber": 24,
        "diningHall": "Central Mess",
        "status": "occupied",
        "entryTime": now_iso,
        "exitTime": None,
    })

    # Force release
    res = client.post(
        "/api/admin/seats/release",
        json={"seatNumber": 24, "reason": "Manager override"},
        headers=admin_headers,
    )
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Verify seat 24 is now free in occupancy
    doc = db_manager.occupancy.find_one({"seatNumber": 24, "status": "occupied"})
    assert doc is None


def test_admin_menu_add_update_delete(client: TestClient):
    """Verify admin can add, update, and delete menu items."""
    admin_headers = {"Authorization": f"Bearer {_get_admin_token()}"}

    # 1. Add menu item
    add_res = client.post(
        "/api/admin/menu/item",
        json={
            "mealType": "Lunch",
            "item": {
                "name": "Kadhai Paneer (Chef Special)",
                "description": "Bell peppers and cottage cheese in spicy wok gravy",
                "category": "Mains",
                "dietary": "Vegetarian",
                "calories": 350,
            },
        },
        headers=admin_headers,
    )
    assert add_res.status_code == 201
    assert add_res.json()["success"] is True

    # 2. Update item
    update_res = client.put(
        "/api/admin/menu/item",
        json={
            "mealType": "Lunch",
            "itemName": "Kadhai Paneer (Chef Special)",
            "item": {
                "name": "Kadhai Paneer (Chef Special)",
                "description": "Extra rich bell pepper and paneer gravy",
                "category": "Mains",
                "dietary": "Vegetarian",
                "calories": 380,
            },
        },
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["success"] is True

    # 3. Delete item
    delete_res = client.request(
        "DELETE",
        "/api/admin/menu/item",
        json={
            "mealType": "Lunch",
            "itemName": "Kadhai Paneer (Chef Special)",
        },
        headers=admin_headers,
    )
    assert delete_res.status_code == 200
    assert delete_res.json()["success"] is True
