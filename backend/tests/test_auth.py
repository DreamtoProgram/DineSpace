from datetime import timedelta
from fastapi.testclient import TestClient
from app.services.security import create_access_token
from tests.conftest import INACTIVE_STUDENT_ID, TEST_PASSWORD, TEST_STUDENT_ID, TEST_STUDENT_NAME


def test_login_success(client: TestClient) -> None:
    """Test 1: Successful login returns 200, JWT token, and public student data."""
    response = client.post(
        "/api/auth/login",
        json={"studentId": TEST_STUDENT_ID, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Login successful"
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    assert data["student"]["studentId"] == TEST_STUDENT_ID
    assert data["student"]["name"] == TEST_STUDENT_NAME
    # Ensure sensitive fields are not leaked
    assert "password" not in data["student"]
    assert "passwordHash" not in data["student"]
    assert "passCode" not in data["student"]


def test_login_wrong_password(client: TestClient) -> None:
    """Test 2: Login with incorrect password returns 401 Unauthorized."""
    response = client.post(
        "/api/auth/login",
        json={"studentId": TEST_STUDENT_ID, "password": "WrongPassword999!"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Invalid student ID or password" in data["detail"]


def test_login_unknown_student(client: TestClient) -> None:
    """Test 3: Login with non-existent student ID returns 401 Unauthorized."""
    response = client.post(
        "/api/auth/login",
        json={"studentId": "STU_DOES_NOT_EXIST", "password": TEST_PASSWORD},
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Invalid student ID or password" in data["detail"]


def test_login_inactive_student(client: TestClient) -> None:
    """Test 4: Login for inactive student returns 403 Forbidden."""
    response = client.post(
        "/api/auth/login",
        json={"studentId": INACTIVE_STUDENT_ID, "password": TEST_PASSWORD},
    )
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert "inactive" in data["detail"].lower()


def test_login_missing_student_id(client: TestClient) -> None:
    """Test 5: Missing studentId fails Pydantic validation with 422."""
    response = client.post(
        "/api/auth/login",
        json={"password": TEST_PASSWORD},
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_login_missing_password(client: TestClient) -> None:
    """Test 6: Missing password fails Pydantic validation with 422."""
    response = client.post(
        "/api/auth/login",
        json={"studentId": TEST_STUDENT_ID},
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_auth_me_success(client: TestClient) -> None:
    """Test 7: GET /api/auth/me with valid Bearer token returns student profile."""
    # First login to obtain token
    login_resp = client.post(
        "/api/auth/login",
        json={"studentId": TEST_STUDENT_ID, "password": TEST_PASSWORD},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["accessToken"]

    # Call /api/auth/me with Bearer token
    me_resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["studentId"] == TEST_STUDENT_ID
    assert data["name"] == TEST_STUDENT_NAME
    # Ensure sensitive fields are not leaked
    assert "password" not in data
    assert "passwordHash" not in data
    assert "passCode" not in data


def test_auth_me_without_token(client: TestClient) -> None:
    """Test 8: GET /api/auth/me without Authorization header returns 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_auth_me_with_invalid_token(client: TestClient) -> None:
    """Test 9: GET /api/auth/me with invalid/garbage token returns 401."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not.a.valid.jwt.token"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_auth_me_with_expired_token(client: TestClient) -> None:
    """Test 10: GET /api/auth/me with expired token returns 401."""
    # Generate an expired token with negative timedelta
    expired_token = create_access_token(
        data={"sub": TEST_STUDENT_ID},
        expires_delta=timedelta(minutes=-10),
    )
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "expired" in data["detail"].lower()


def test_auth_me_inactive_student_token(client: TestClient) -> None:
    """Test 11: GET /api/auth/me with valid token for inactive student returns 403."""
    inactive_token = create_access_token(data={"sub": INACTIVE_STUDENT_ID})
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {inactive_token}"},
    )
    assert response.status_code == 403
    data = response.json()
    assert "inactive" in data["detail"].lower()
