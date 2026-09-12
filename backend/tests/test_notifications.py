from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from app.services.menu_service import get_campus_timezone
from app.services.notification_service import (
    create_notification,
    ensure_notification_indexes,
)
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token
from app.services.timeout_service import expire_abandoned_visits
from tests.conftest import TEST_STUDENT_ID

OTHER_STUDENT_ID = "STU1043"


@pytest.fixture(autouse=True)
def setup_collections():
    """Clean up notifications and occupancy collections and ensure indexes before each test."""
    db_manager.notifications.delete_many({})
    db_manager.occupancy.delete_many({})
    ensure_occupancy_indexes()
    ensure_notification_indexes()
    yield
    db_manager.notifications.delete_many({})
    db_manager.occupancy.delete_many({})


def _get_token(student_id: str) -> str:
    """Helper to generate a valid access token."""
    return create_access_token(data={"sub": student_id})


def test_student_retrieves_notifications(client: TestClient):
    """TEST 1: Authenticated student can retrieve their notifications."""
    create_notification(
        student_id=TEST_STUDENT_ID,
        notification_type="system",
        title="Welcome",
        message="Welcome to DineSpace!",
    )

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["title"] == "Welcome"
    assert data["notifications"][0]["type"] == "system"
    assert data["unreadCount"] == 1
    assert data["pagination"]["total"] == 1


def test_cross_student_isolation(client: TestClient):
    """TEST 2: Student A cannot retrieve Student B's notifications."""
    create_notification(
        student_id=TEST_STUDENT_ID,
        notification_type="visit",
        title="Student A Alert",
        message="Message for A",
    )
    create_notification(
        student_id=OTHER_STUDENT_ID,
        notification_type="visit",
        title="Student B Alert",
        message="Message for B",
    )

    token_a = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/notifications", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["title"] == "Student A Alert"


def test_notifications_sorted_newest_first(client: TestClient):
    """TEST 3: Notifications are sorted newest first by createdAt descending."""
    now = datetime.now(get_campus_timezone())

    # Insert older first, then newer
    db_manager.notifications.insert_many([
        {
            "studentId": TEST_STUDENT_ID,
            "type": "menu",
            "title": "Older Alert",
            "message": "First",
            "createdAt": (now - timedelta(hours=2)).isoformat(),
            "read": False,
            "metadata": {},
        },
        {
            "studentId": TEST_STUDENT_ID,
            "type": "menu",
            "title": "Newer Alert",
            "message": "Second",
            "createdAt": (now - timedelta(minutes=10)).isoformat(),
            "read": False,
            "metadata": {},
        },
    ])

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    items = res.json()["notifications"]
    assert len(items) == 2
    assert items[0]["title"] == "Newer Alert"
    assert items[1]["title"] == "Older Alert"


def test_pagination_limit(client: TestClient):
    """TEST 4: Pagination limit restricts number of items returned."""
    for i in range(5):
        create_notification(
            student_id=TEST_STUDENT_ID,
            notification_type="system",
            title=f"Notification {i}",
            message="Test",
        )

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/notifications?limit=2", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["notifications"]) == 2
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["total"] == 5


def test_pagination_offset(client: TestClient):
    """TEST 5: Pagination offset skips the specified number of items."""
    now = datetime.now(get_campus_timezone())
    for i in range(3):
        db_manager.notifications.insert_one({
            "studentId": TEST_STUDENT_ID,
            "type": "system",
            "title": f"Note {i}",
            "message": "Test",
            "createdAt": (now - timedelta(hours=3 - i)).isoformat(),
            "read": False,
            "metadata": {},
        })

    token = _get_token(TEST_STUDENT_ID)
    # limit=1, offset=1 should skip the newest (Note 2) and return Note 1
    res = client.get("/api/notifications?limit=1&offset=1", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["notifications"]) == 1
    assert data["notifications"][0]["title"] == "Note 1"
    assert data["pagination"]["offset"] == 1


def test_invalid_limit_rejected(client: TestClient):
    """TEST 6: Invalid limit (0 or >100) returns 422."""
    token = _get_token(TEST_STUDENT_ID)
    res_zero = client.get("/api/notifications?limit=0", headers={"Authorization": f"Bearer {token}"})
    assert res_zero.status_code == 422

    res_too_high = client.get("/api/notifications?limit=101", headers={"Authorization": f"Bearer {token}"})
    assert res_too_high.status_code == 422


def test_invalid_offset_rejected(client: TestClient):
    """TEST 7: Negative offset returns 422."""
    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/notifications?offset=-1", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422


def test_notification_type_filter(client: TestClient):
    """TEST 8: Filtering by notification type returns only matching items."""
    create_notification(TEST_STUDENT_ID, "menu", "Menu Update", "Paneer today")
    create_notification(TEST_STUDENT_ID, "crowd", "Crowd Rush", "Central mess 85%")
    create_notification(TEST_STUDENT_ID, "visit", "Visit Started", "Checked in")
    create_notification(TEST_STUDENT_ID, "system", "System Notice", "Maintenance")

    token = _get_token(TEST_STUDENT_ID)

    # Filter menu
    res_menu = client.get("/api/notifications?type=menu", headers={"Authorization": f"Bearer {token}"})
    assert res_menu.status_code == 200
    assert len(res_menu.json()["notifications"]) == 1
    assert res_menu.json()["notifications"][0]["type"] == "menu"

    # Filter crowd
    res_crowd = client.get("/api/notifications?type=crowd", headers={"Authorization": f"Bearer {token}"})
    assert res_crowd.status_code == 200
    assert len(res_crowd.json()["notifications"]) == 1
    assert res_crowd.json()["notifications"][0]["type"] == "crowd"

    # Filter all
    res_all = client.get("/api/notifications?type=all", headers={"Authorization": f"Bearer {token}"})
    assert res_all.status_code == 200
    assert len(res_all.json()["notifications"]) == 4


def test_invalid_notification_type_rejected(client: TestClient):
    """TEST 9: Invalid category filter type returns 400 Bad Request."""
    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/notifications?type=unknown_category", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    assert "Invalid notification type" in res.json()["detail"]


def test_unread_count_accurate(client: TestClient):
    """TEST 10: unreadCount correctly reflects unread alerts across all categories."""
    create_notification(TEST_STUDENT_ID, "menu", "Menu 1", "desc")
    create_notification(TEST_STUDENT_ID, "crowd", "Crowd 1", "desc")
    notif3 = create_notification(TEST_STUDENT_ID, "system", "System 1", "desc")

    # Mark notif3 as read in DB directly
    db_manager.notifications.update_one({"_id": ObjectId(notif3["id"])}, {"$set": {"read": True}})

    token = _get_token(TEST_STUDENT_ID)
    res = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    # Total 3 notifications, 2 are unread
    assert res.json()["unreadCount"] == 2


def test_mark_single_notification_read(client: TestClient):
    """TEST 11: Student can mark their notification as read via PATCH."""
    notif = create_notification(TEST_STUDENT_ID, "visit", "Visit Done", "Desc")
    notif_id = notif["id"]

    token = _get_token(TEST_STUDENT_ID)
    res = client.patch(
        f"/api/notifications/{notif_id}/read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["notification"]["id"] == notif_id
    assert data["notification"]["read"] is True

    # Verify in DB
    doc = db_manager.notifications.find_one({"_id": ObjectId(notif_id)})
    assert doc["read"] is True


def test_mark_already_read_idempotent(client: TestClient):
    """TEST 12: Marking an already-read notification is idempotent."""
    notif = create_notification(TEST_STUDENT_ID, "visit", "Visit Done", "Desc")
    notif_id = notif["id"]
    token = _get_token(TEST_STUDENT_ID)

    # First mark
    res1 = client.patch(f"/api/notifications/{notif_id}/read", headers={"Authorization": f"Bearer {token}"})
    assert res1.status_code == 200

    # Second mark
    res2 = client.patch(f"/api/notifications/{notif_id}/read", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 200
    assert res2.json()["notification"]["read"] is True


def test_student_cannot_mark_other_student_notification(client: TestClient):
    """TEST 13: Student A cannot mark Student B's notification as read (returns 404)."""
    notif_b = create_notification(OTHER_STUDENT_ID, "visit", "Student B Alert", "Private")
    notif_b_id = notif_b["id"]

    token_a = _get_token(TEST_STUDENT_ID)
    res = client.patch(
        f"/api/notifications/{notif_b_id}/read",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "Notification not found."

    # Verify B's notification is still unread
    doc_b = db_manager.notifications.find_one({"_id": ObjectId(notif_b_id)})
    assert doc_b["read"] is False


def test_mark_all_read_authenticated_student_only(client: TestClient):
    """TEST 14: mark-all-read marks all unread notifications of authenticated student only."""
    create_notification(TEST_STUDENT_ID, "menu", "A1", "msg")
    create_notification(TEST_STUDENT_ID, "visit", "A2", "msg")
    notif_b = create_notification(OTHER_STUDENT_ID, "system", "B1", "msg")

    token_a = _get_token(TEST_STUDENT_ID)
    res = client.patch("/api/notifications/read-all", headers={"Authorization": f"Bearer {token_a}"})
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["updatedCount"] == 2

    # A's unread count is now 0
    res_a = client.get("/api/notifications", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.json()["unreadCount"] == 0

    # B's notification is still unread
    doc_b = db_manager.notifications.find_one({"_id": ObjectId(notif_b["id"])})
    assert doc_b["read"] is False


def test_mark_all_read_idempotent(client: TestClient):
    """TEST 15: mark-all-read is idempotent, returns updatedCount=0 when none unread."""
    create_notification(TEST_STUDENT_ID, "menu", "A1", "msg")
    token = _get_token(TEST_STUDENT_ID)

    res1 = client.patch("/api/notifications/read-all", headers={"Authorization": f"Bearer {token}"})
    assert res1.json()["updatedCount"] == 1

    res2 = client.patch("/api/notifications/read-all", headers={"Authorization": f"Bearer {token}"})
    assert res2.json()["updatedCount"] == 0


def test_completed_visit_creates_one_notification(client: TestClient):
    """TEST 16: Completed visit via tray return creates exactly one visit notification."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=15)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 24,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    exit_res = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert exit_res.status_code == 200

    # Verify notification created
    notifs = list(db_manager.notifications.find({"studentId": TEST_STUDENT_ID}))
    assert len(notifs) == 1
    assert notifs[0]["type"] == "visit"
    assert notifs[0]["title"] == "Visit completed"
    assert notifs[0]["metadata"]["seatNumber"] == 24
    assert notifs[0]["metadata"]["exitReason"] == "tray_return"


def test_timed_out_visit_creates_one_notification():
    """TEST 17: Timed-out visit creates exactly one visit notification."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=30)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 30,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    expired = expire_abandoned_visits(now_dt=now, timeout_minutes=25)
    assert expired == 1

    notifs = list(db_manager.notifications.find({"studentId": TEST_STUDENT_ID}))
    assert len(notifs) == 1
    assert notifs[0]["type"] == "visit"
    assert notifs[0]["title"] == "Visit timed out"
    assert notifs[0]["metadata"]["seatNumber"] == 30
    assert notifs[0]["metadata"]["exitReason"] == "timeout"


def test_failed_concurrent_state_transition_no_duplicate_notification(client: TestClient):
    """TEST 18: Repeated or failed exit requests do NOT create duplicate notifications."""
    now = datetime.now(get_campus_timezone())
    entry_time = (now - timedelta(minutes=15)).isoformat()

    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 10,
        "diningHall": "Central Mess",
        "entryTime": entry_time,
        "exitTime": None,
        "status": "occupied",
        "mealType": "Lunch",
    })

    token = _get_token(TEST_STUDENT_ID)
    # First exit succeeds -> creates 1 notification
    res1 = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert res1.status_code == 200

    # Immediate second exit fails with 409 Conflict
    res2 = client.post("/api/scan/exit", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 409

    # Total notifications must remain strictly 1
    count = db_manager.notifications.count_documents({"studentId": TEST_STUDENT_ID})
    assert count == 1


def test_unauthenticated_notification_requests_rejected(client: TestClient):
    """TEST 19: Unauthenticated requests to notification endpoints are rejected with 401."""
    assert client.get("/api/notifications").status_code == 401
    assert client.patch("/api/notifications/read-all").status_code == 401
    assert client.patch("/api/notifications/123/read").status_code == 401


def test_notification_response_no_mongo_id_leaked(client: TestClient):
    """TEST 20: Notification response does not expose internal MongoDB _id."""
    create_notification(TEST_STUDENT_ID, "system", "Test ID", "Message")
    token = _get_token(TEST_STUDENT_ID)

    res = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    item = data["notifications"][0]

    assert "_id" not in item
    assert "_id" not in data
    assert "id" in item
    assert isinstance(item["id"], str)
