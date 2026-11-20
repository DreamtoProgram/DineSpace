from fastapi.testclient import TestClient
import pytest

from app.database import db_manager


def test_google_sso_login_existing_student(client: TestClient) -> None:
    """Test 1: Login via Google Workspace SSO for an existing student."""
    response = client.post(
        "/api/auth/sso/login",
        json={
            "provider": "google",
            "email": "sarah.chen@university.edu",
            "name": "Sarah Chen",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "accessToken" in data
    assert data["student"]["studentId"] == "STU1042"
    assert data["student"]["name"] == "Sarah Chen"
    assert data["student"]["rfidCardUid"] == "CARD-8842-A1"


def test_microsoft_sso_login_existing_student(client: TestClient) -> None:
    """Test 2: Login via Microsoft 365 for Education SSO."""
    response = client.post(
        "/api/auth/sso/login",
        json={
            "provider": "microsoft",
            "email": "kunal.singh@university.edu",
            "name": "Kunal Kumar Singh",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["student"]["studentId"] == "P132-NNK"
    assert data["student"]["name"] == "Kunal Kumar Singh"
    assert data["student"]["rfidCardUid"] == "CARD-1042-B2"


def test_sso_login_new_student_auto_provisioning(client: TestClient) -> None:
    """Test 3: Auto-provisioning for a new student logging in via institutional SSO."""
    response = client.post(
        "/api/auth/sso/login",
        json={
            "provider": "campus_erp",
            "email": "aarav.patel@university.edu",
            "name": "Aarav Patel",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["student"]["studentId"].startswith("SSO")
    assert data["student"]["name"] == "Aarav Patel"
    assert data["student"]["email"] == "aarav.patel@university.edu"


def test_sso_invalid_provider_returns_400(client: TestClient) -> None:
    """Test 4: Unsupported SSO provider returns 400 Bad Request."""
    response = client.post(
        "/api/auth/sso/login",
        json={
            "provider": "unsupported_oauth_vendor",
            "email": "test@unknown.com",
        },
    )
    assert response.status_code == 400
    assert "Unsupported SSO provider" in response.json()["detail"]


def test_sso_inactive_student_returns_403(client: TestClient) -> None:
    """Test 5: Inactive student account attempting SSO returns 403 Forbidden."""
    response = client.post(
        "/api/auth/sso/login",
        json={
            "provider": "google",
            "email": "inactive@university.edu",
        },
    )
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_rfid_tap_login_success(client: TestClient) -> None:
    """Test 6: Tap registered physical RFID student badge to authenticate."""
    response = client.post(
        "/api/auth/rfid/tap",
        json={"cardUid": "CARD-8842-A1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["student"]["studentId"] == "STU1042"
    assert data["student"]["name"] == "Sarah Chen"
    assert "accessToken" in data


def test_rfid_tap_unregistered_card_returns_404(client: TestClient) -> None:
    """Test 7: Unregistered RFID card badge returns 404 Not Found."""
    response = client.post(
        "/api/auth/rfid/tap",
        json={"cardUid": "CARD-UNKNOWN-999"},
    )
    assert response.status_code == 404
    assert "Unrecognized RFID" in response.json()["detail"]


def test_rfid_tap_deactivated_card_returns_403(client: TestClient) -> None:
    """Test 8: Deactivated student card returns 403 Forbidden."""
    response = client.post(
        "/api/auth/rfid/tap",
        json={"cardUid": "CARD-9999-XX"},
    )
    assert response.status_code == 403


def test_nfc_kiosk_entry_scan_allocates_seat(client: TestClient) -> None:
    """Test 9: 1-Tap physical RFID card checkin at entrance kiosk assigns seat."""
    db_manager.occupancy.delete_many({})

    response = client.post(
        "/api/scan/nfc-entry",
        json={
            "cardUid": "CARD-8842-A1",
            "diningHall": "Central Mess",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["student"]["studentId"] == "STU1042"
    assert data["seatNumber"] >= 1
    assert data["diningHall"] == "Central Mess"
    assert "entryTime" in data

    # Verify active visit recorded
    record = db_manager.occupancy.find_one({"studentId": "STU1042", "status": "occupied"})
    assert record is not None
    assert record["seatNumber"] == data["seatNumber"]


def test_nfc_kiosk_entry_duplicate_active_visit_conflict(client: TestClient) -> None:
    """Test 10: Tapping card again while already dining returns 409 Conflict."""
    db_manager.occupancy.delete_many({})

    # First tap succeeds
    res1 = client.post(
        "/api/scan/nfc-entry",
        json={"cardUid": "CARD-1042-B2", "diningHall": "Central Mess"},
    )
    assert res1.status_code == 200

    # Second tap fails with 409 active visit conflict
    res2 = client.post(
        "/api/scan/nfc-entry",
        json={"cardUid": "CARD-1042-B2", "diningHall": "Central Mess"},
    )
    assert res2.status_code == 409
    assert "already have an active" in res2.json()["detail"].lower()
