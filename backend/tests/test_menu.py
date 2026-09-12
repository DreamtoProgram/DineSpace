from fastapi.testclient import TestClient
import pytest
from app.database import db_manager
from app.services.menu_service import get_today_date_str, upsert_menu


def test_get_today_menu_success(client: TestClient) -> None:
    """Test 1: GET /api/menu/today returns 200 and today's Lunch and Dinner."""
    response = client.get("/api/menu/today")
    assert response.status_code == 200
    data = response.json()
    assert "date" in data
    assert data["date"] == get_today_date_str()
    assert "menus" in data
    assert len(data["menus"]) == 2

    # Verify Lunch and Dinner meals
    meal_types = [m["mealType"] for m in data["menus"]]
    assert "Lunch" in meal_types
    assert "Dinner" in meal_types

    # Verify specific dishes matching designed page
    lunch_menu = next(m for m in data["menus"] if m["mealType"] == "Lunch")
    lunch_item_names = [i["name"] for i in lunch_menu["items"]]
    assert "Paneer Butter Masala" in lunch_item_names
    assert "Dal Tadka" in lunch_item_names
    assert "Steamed Rice" in lunch_item_names
    assert "Roti" in lunch_item_names
    assert "Gulab Jamun" in lunch_item_names


def test_get_menu_by_date(client: TestClient) -> None:
    """Test 2 & 7: GET /api/menu?date=... returns all meals for that date."""
    today = get_today_date_str()
    response = client.get(f"/api/menu?date={today}")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == today
    assert len(data["menus"]) == 2


def test_get_menu_by_date_and_meal_type(client: TestClient) -> None:
    """Test 3: GET /api/menu?date=...&mealType=Lunch returns single Lunch menu."""
    today = get_today_date_str()
    response = client.get(f"/api/menu?date={today}&mealType=Lunch")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == today
    assert data["mealType"] == "Lunch"
    assert "items" in data
    assert len(data["items"]) == 5
    assert data["items"][0]["name"] == "Paneer Butter Masala"
    assert data["items"][0]["description"] == "A classic favorite"


def test_get_menu_nonexistent_date(client: TestClient) -> None:
    """Test 4: GET /api/menu for a date with no record returns 404."""
    response = client.get("/api/menu?date=2099-01-01")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "No menus found" in data["detail"]


def test_get_menu_nonexistent_meal_type_for_date(client: TestClient) -> None:
    """Test 4b: GET /api/menu for valid date but non-existent meal returns 404."""
    response = client.get("/api/menu?date=2026-09-10&mealType=Dinner")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "No Dinner menu found" in data["detail"]


def test_get_menu_invalid_date_format(client: TestClient) -> None:
    """Test 5: GET /api/menu with invalid calendar date returns 422."""
    response = client.get("/api/menu?date=2026-99-99")
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_get_menu_invalid_meal_type(client: TestClient) -> None:
    """Test 6: GET /api/menu with unsupported mealType returns 422."""
    response = client.get("/api/menu?date=2026-09-12&mealType=MidnightSnack")
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_menu_schema_validation(client: TestClient) -> None:
    """Test 8: Schema structure of menu items matches requirements."""
    response = client.get("/api/menu/today")
    assert response.status_code == 200
    data = response.json()
    for menu in data["menus"]:
        assert menu["mealType"] in ["Lunch", "Dinner"]
        for item in menu["items"]:
            assert isinstance(item["name"], str)
            assert len(item["name"]) > 0
            assert isinstance(item["description"], str)


def test_seed_menu_upsert_no_duplicates() -> None:
    """Test 9: Re-running upsert does not create duplicate entries for same date & meal."""
    test_date = "2026-10-15"
    meal = "Lunch"
    items = [{"name": "Rajma Chawal", "description": "Kidney beans with steamed rice"}]

    # First upsert
    upsert_menu(test_date, meal, items)
    count_1 = db_manager.menu.count_documents({"date": test_date, "mealType": meal})
    assert count_1 == 1

    # Second upsert (re-seed)
    upsert_menu(test_date, meal, items)
    count_2 = db_manager.menu.count_documents({"date": test_date, "mealType": meal})
    assert count_2 == 1
