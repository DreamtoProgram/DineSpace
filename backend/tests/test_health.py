from fastapi.testclient import TestClient
from app.database import db_manager


def test_health_check_returns_200_and_expected_payload(client: TestClient) -> None:
    """Ensure GET /api/health returns 200 OK and expected payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ok",
        "service": "dinespace-backend",
    }


def test_cors_headers_configured(client: TestClient) -> None:
    """Ensure CORS headers are returned for allowed origins."""
    origin = "http://localhost:3000"
    response = client.get("/api/health", headers={"Origin": origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin


def test_not_found_endpoint(client: TestClient) -> None:
    """Ensure requests to undefined endpoints return 404."""
    response = client.get("/api/nonexistent-route")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_database_manager_collection_attributes() -> None:
    """Ensure DatabaseManager exposes required core collections."""
    assert hasattr(db_manager, "students")
    assert hasattr(db_manager, "occupancy")
    assert hasattr(db_manager, "menu")
    assert hasattr(db_manager, "ping")
    assert hasattr(db_manager, "connect")
    assert hasattr(db_manager, "close")
