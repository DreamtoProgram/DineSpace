from typing import Generator
import mongomock
import pytest
from fastapi.testclient import TestClient

from app.database import db_manager
from app.main import app
from app.services.menu_service import get_today_date_str
from app.services.security import hash_password

TEST_STUDENT_ID = "STU1042"
TEST_STUDENT_NAME = "Sarah Chen"
TEST_PASSWORD = "ValidPassword123!"
INACTIVE_STUDENT_ID = "STU9999"


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch: pytest.MonkeyPatch):
    """Isolate tests using an in-memory mongomock database instance."""
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["dinespace_test"]

    # Prevent lifespan from attempting to connect to or close real MongoDB during tests
    monkeypatch.setattr(db_manager, "connect", lambda *args, **kwargs: None)
    monkeypatch.setattr(db_manager, "close", lambda *args, **kwargs: None)
    monkeypatch.setattr(db_manager, "ping", lambda *args, **kwargs: True)

    # Seed test student records
    password_hash = hash_password(TEST_PASSWORD)
    mock_db.students.insert_many([
        {
            "studentId": TEST_STUDENT_ID,
            "name": TEST_STUDENT_NAME,
            "passCode": "PASS-8842",
            "passwordHash": password_hash,
            "isActive": True,
        },
        {
            "studentId": "STU1043",
            "name": "Alex Sharma",
            "passCode": "PASS-8843",
            "passwordHash": password_hash,
            "isActive": True,
        },
        {
            "studentId": INACTIVE_STUDENT_ID,
            "name": "Inactive Student",
            "passCode": "PASS-9999",
            "passwordHash": password_hash,
            "isActive": False,
        },
    ])

    # Seed test menus (Today's Lunch & Dinner + historical date)
    today = get_today_date_str()
    mock_db.menu.insert_many([
        {
            "date": today,
            "mealType": "Lunch",
            "items": [
                {"name": "Paneer Butter Masala", "description": "A classic favorite"},
                {"name": "Dal Tadka", "description": "Protein rich and wholesome"},
                {"name": "Steamed Rice", "description": "Light and healthy"},
                {"name": "Roti", "description": "Freshly made"},
                {"name": "Gulab Jamun", "description": "Because every meal deserves a sweet ending"},
            ],
        },
        {
            "date": today,
            "mealType": "Dinner",
            "items": [
                {"name": "Shahi Paneer", "description": "Rich and aromatic cottage cheese gravy"},
                {"name": "Mixed Dal Tadka", "description": "Slow-cooked savory lentils"},
                {"name": "Jeera Rice", "description": "Fragrant cumin tempered basmati rice"},
                {"name": "Butter Naan", "description": "Crispy and soft tandoor-baked flatbread"},
                {"name": "Rasgulla", "description": "Traditional sweet cottage cheese dumplings"},
            ],
        },
        {
            "date": "2026-09-10",
            "mealType": "Lunch",
            "items": [
                {"name": "Chole Bhature", "description": "Spiced chickpeas with fried bread"},
            ],
        },
    ])

    original_client = db_manager.client
    original_db = db_manager.db
    db_manager.client = mock_client
    db_manager.db = mock_db

    yield mock_db

    db_manager.client = original_client
    db_manager.db = original_db


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Provide a TestClient instance for testing API endpoints."""
    with TestClient(app) as test_client:
        yield test_client
