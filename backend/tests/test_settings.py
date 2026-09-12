from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.notification_service import create_notification, get_student_notifications
from app.services.security import create_access_token, verify_password
from tests.conftest import INACTIVE_STUDENT_ID, TEST_PASSWORD, TEST_STUDENT_ID, TEST_STUDENT_NAME


def _get_token(student_id: str) -> str:
    """Generate a valid JWT bearer token for testing."""
    return create_access_token(data={"sub": student_id})


def _auth_header(student_id: str = TEST_STUDENT_ID) -> dict:
    """Generate the Authorization header dictionary."""
    return {"Authorization": f"Bearer {_get_token(student_id)}"}


# TEST 1: Authenticated student can retrieve their settings
def test_get_settings_success(client: TestClient):
    response = client.get("/api/settings", headers=_auth_header(TEST_STUDENT_ID))
    assert response.status_code == 200
    data = response.json()
    assert data["student"]["studentId"] == TEST_STUDENT_ID
    assert data["student"]["name"] == TEST_STUDENT_NAME
    assert data["diningHall"] == "Central Mess"
    assert data["preferences"]["notificationsEnabled"] is True


# TEST 2: Unauthenticated GET /api/settings is rejected
def test_get_settings_unauthenticated_rejected(client: TestClient):
    # No header
    response = client.get("/api/settings")
    assert response.status_code == 401

    # Invalid header
    response = client.get("/api/settings", headers={"Authorization": "Bearer bad.token.xyz"})
    assert response.status_code == 401


# TEST 3: Student A cannot access Student B's settings
def test_get_settings_student_isolation(client: TestClient):
    # Student A requests settings
    response_a = client.get("/api/settings", headers=_auth_header(TEST_STUDENT_ID))
    assert response_a.status_code == 200
    data_a = response_a.json()
    assert data_a["student"]["studentId"] == TEST_STUDENT_ID
    assert data_a["student"]["name"] == TEST_STUDENT_NAME

    # Attempting to pass query param studentId is ignored
    response_spoof = client.get(
        f"/api/settings?studentId=STU1043",
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert response_spoof.status_code == 200
    data_spoof = response_spoof.json()
    assert data_spoof["student"]["studentId"] == TEST_STUDENT_ID
    assert "STU1043" not in data_spoof["student"]["studentId"]


# TEST 4: Supported preference can be updated
def test_patch_settings_update_preference(client: TestClient):
    # Update to False
    response = client.patch(
        "/api/settings",
        json={"notificationsEnabled": False},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["preferences"]["notificationsEnabled"] is False

    # Update back to True
    response_true = client.patch(
        "/api/settings",
        json={"notificationsEnabled": True},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert response_true.status_code == 200
    assert response_true.json()["preferences"]["notificationsEnabled"] is True


# TEST 5: Updated preference is persisted in MongoDB
def test_patch_settings_persisted_in_mongodb(client: TestClient):
    client.patch(
        "/api/settings",
        json={"notificationsEnabled": False},
        headers=_auth_header(TEST_STUDENT_ID),
    )

    doc = db_manager.students.find_one({"studentId": TEST_STUDENT_ID})
    assert doc is not None
    assert doc.get("preferences", {}).get("notificationsEnabled") is False


# TEST 6: Unsupported/arbitrary fields cannot be written
def test_patch_settings_arbitrary_fields_rejected(client: TestClient):
    response = client.patch(
        "/api/settings",
        json={"role": "admin", "notificationsEnabled": True},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert response.status_code == 422

    # Verify 'role' was not written to MongoDB
    doc = db_manager.students.find_one({"studentId": TEST_STUDENT_ID})
    assert "role" not in doc


# TEST 7: Student ID cannot be changed through settings
def test_patch_settings_student_id_immutable(client: TestClient):
    response = client.patch(
        "/api/settings",
        json={"studentId": "HACKED_ID", "notificationsEnabled": False},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert response.status_code == 422

    # Verify student ID remains TEST_STUDENT_ID
    doc = db_manager.students.find_one({"studentId": TEST_STUDENT_ID})
    assert doc is not None
    assert doc["studentId"] == TEST_STUDENT_ID


# TEST 8: Name/profile information is returned correctly
def test_get_settings_profile_data_accurate(client: TestClient):
    response = client.get("/api/settings", headers=_auth_header("STU1043"))
    assert response.status_code == 200
    data = response.json()
    assert data["student"]["studentId"] == "STU1043"
    assert data["student"]["name"] == "Alex Sharma"


# TEST 9: Response does not expose passwordHash
def test_get_settings_no_password_hash_leak(client: TestClient):
    response = client.get("/api/settings", headers=_auth_header(TEST_STUDENT_ID))
    assert response.status_code == 200
    text = response.text
    assert "passwordHash" not in text
    assert "$2b$" not in text


# TEST 10: Response does not expose passCode
def test_get_settings_no_pass_code_leak(client: TestClient):
    response = client.get("/api/settings", headers=_auth_header(TEST_STUDENT_ID))
    assert response.status_code == 200
    text = response.text
    assert "passCode" not in text
    assert "PASS-8842" not in text


# TEST 11: Password change functionality
def test_change_password_success_and_failure(client: TestClient):
    new_pwd = "BrandNewPassword2026!"

    # 1. Incorrect current password fails
    bad_res = client.patch(
        "/api/settings/password",
        json={"currentPassword": "WrongCurrentPassword!", "newPassword": new_pwd},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert bad_res.status_code == 400
    assert "Current password is incorrect" in bad_res.json()["detail"]

    # 2. Correct current password succeeds
    good_res = client.patch(
        "/api/settings/password",
        json={"currentPassword": TEST_PASSWORD, "newPassword": new_pwd},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert good_res.status_code == 200
    data = good_res.json()
    assert data["success"] is True
    assert "Password changed successfully" in data["message"]

    # 3. Verify in MongoDB: securely hashed and plaintext is never stored
    doc = db_manager.students.find_one({"studentId": TEST_STUDENT_ID})
    assert doc is not None
    assert doc["passwordHash"] != TEST_PASSWORD
    assert doc["passwordHash"] != new_pwd
    assert verify_password(new_pwd, doc["passwordHash"]) is True
    assert "newPassword" not in doc
    assert "currentPassword" not in doc


# TEST 12: Password hash changes and subsequent login behavior
def test_change_password_login_verification(client: TestClient):
    new_pwd = "UpdatedSecurePassword999!"

    # Change password
    res = client.patch(
        "/api/settings/password",
        json={"currentPassword": TEST_PASSWORD, "newPassword": new_pwd},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert res.status_code == 200

    # Old password no longer authenticates
    old_login = client.post(
        "/api/auth/login",
        json={"studentId": TEST_STUDENT_ID, "password": TEST_PASSWORD},
    )
    assert old_login.status_code == 401

    # New password successfully authenticates
    new_login = client.post(
        "/api/auth/login",
        json={"studentId": TEST_STUDENT_ID, "password": new_pwd},
    )
    assert new_login.status_code == 200
    assert "accessToken" in new_login.json()


# TEST 13: Notification preference persists and controls future notifications
def test_notification_preference_suppresses_future_notifications(client: TestClient):
    # 1. Ensure initial notification can be created
    notif1 = create_notification(TEST_STUDENT_ID, "system", "First Alert", "Hello")
    assert notif1 is not None

    # 2. Disable notifications via Settings
    patch_res = client.patch(
        "/api/settings",
        json={"notificationsEnabled": False},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert patch_res.status_code == 200

    # 3. Future notification creation is suppressed
    notif2 = create_notification(TEST_STUDENT_ID, "system", "Suppressed Alert", "Should not be created")
    assert notif2 is None

    # 4. Existing notification is NOT deleted
    list_res = get_student_notifications(TEST_STUDENT_ID)
    assert list_res.pagination.total == 1
    assert list_res.notifications[0].title == "First Alert"

    # 5. Re-enable notifications
    client.patch(
        "/api/settings",
        json={"notificationsEnabled": True},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    notif3 = create_notification(TEST_STUDENT_ID, "system", "Third Alert", "Active again")
    assert notif3 is not None
    assert get_student_notifications(TEST_STUDENT_ID).pagination.total == 2


# TEST 14: Student A cannot modify Student B's preferences
def test_patch_settings_student_isolation(client: TestClient):
    # Student A sets notifications to False
    client.patch(
        "/api/settings",
        json={"notificationsEnabled": False},
        headers=_auth_header(TEST_STUDENT_ID),
    )

    # Student B's preferences remain default True
    doc_b = db_manager.students.find_one({"studentId": "STU1043"})
    assert doc_b.get("preferences", {}).get("notificationsEnabled") is not False

    res_b = client.get("/api/settings", headers=_auth_header("STU1043"))
    assert res_b.json()["preferences"]["notificationsEnabled"] is True


# TEST 15: Malformed settings values are rejected
def test_patch_settings_malformed_values_rejected(client: TestClient):
    # Invalid boolean
    bad_type_res = client.patch(
        "/api/settings",
        json={"notificationsEnabled": "not-a-boolean"},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert bad_type_res.status_code == 422

    # Malformed password change (empty strings)
    bad_pwd_res = client.patch(
        "/api/settings/password",
        json={"currentPassword": "", "newPassword": ""},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert bad_pwd_res.status_code == 422


# TEST 16: Inactive student account is rejected
def test_settings_inactive_student_rejected(client: TestClient):
    get_res = client.get("/api/settings", headers=_auth_header(INACTIVE_STUDENT_ID))
    assert get_res.status_code == 403

    patch_res = client.patch(
        "/api/settings",
        json={"notificationsEnabled": False},
        headers=_auth_header(INACTIVE_STUDENT_ID),
    )
    assert patch_res.status_code == 403

    pwd_res = client.patch(
        "/api/settings/password",
        json={"currentPassword": TEST_PASSWORD, "newPassword": "NewPassword123!"},
        headers=_auth_header(INACTIVE_STUDENT_ID),
    )
    assert pwd_res.status_code == 403


# TEST 17: Nested preferences object update format supported
def test_patch_settings_nested_preferences_format(client: TestClient):
    response = client.patch(
        "/api/settings",
        json={"preferences": {"notificationsEnabled": False}},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert response.status_code == 200
    assert response.json()["preferences"]["notificationsEnabled"] is False
