from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import pytest

from app.database import db_manager
from scripts.seed_menu import seed as seed_menu_fn
from scripts.seed_students import seed as seed_students_fn
from app.services.occupancy_service import ensure_occupancy_indexes
from app.services.security import create_access_token
from app.services.timeout_service import expire_abandoned_visits
from app.services.visit_service import complete_current_visit
from tests.conftest import TEST_PASSWORD, TEST_STUDENT_ID, TEST_STUDENT_NAME


@pytest.fixture(autouse=True)
def clean_db():
    """Ensure a clean database state before each integration test."""
    db_manager.occupancy.delete_many({})
    db_manager.notifications.delete_many({})
    ensure_occupancy_indexes()
    yield
    db_manager.occupancy.delete_many({})
    db_manager.notifications.delete_many({})


def _auth_header(student_id: str = TEST_STUDENT_ID) -> dict:
    """Helper to return Bearer JWT Authorization header."""
    token = create_access_token(data={"sub": student_id})
    return {"Authorization": f"Bearer {token}"}


# 1. Complete Student Demo Journey
def test_e2e_student_lifecycle_journey(client: TestClient):
    """E2E Test 1: Complete student dining flow from login to exit, history, and notifications."""
    # Step 1: Login
    login_res = client.post(
        "/api/auth/login",
        json={"studentId": TEST_STUDENT_ID, "password": TEST_PASSWORD},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    token = login_data["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Verify Profile via /api/auth/me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["studentId"] == TEST_STUDENT_ID
    assert me_res.json()["name"] == TEST_STUDENT_NAME

    # Step 3: Check Menu
    menu_res = client.get("/api/menu/today")
    assert menu_res.status_code == 200
    assert "menus" in menu_res.json()

    # Step 4: Check Status before entry (clean slate)
    status_0 = client.get("/api/status").json()
    assert status_0["occupiedSeats"] == 0
    assert status_0["availableSeats"] == 100
    assert status_0["crowdLevel"] == "Low"

    # Step 5: Check Seats before entry
    seats_0 = client.get("/api/seats", headers=headers).json()
    assert seats_0["occupiedCount"] == 0
    assert seats_0["availableCount"] == 100
    assert seats_0["mySeat"] is None
    assert seats_0["nextAvailableSeat"] == 1

    # Step 6: Check Current Visit (inactive)
    visit_0 = client.get("/api/visits/current", headers=headers).json()
    assert visit_0["active"] is False
    assert visit_0["visit"] is None

    # Step 7: Entry Scan (QR check-in)
    entry_res = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8842"},
        headers=headers,
    )
    assert entry_res.status_code == 200
    entry_data = entry_res.json()
    assigned_seat = entry_data["seatNumber"]
    assert assigned_seat == 1
    assert entry_data["diningHall"] == "Central Mess"

    # Step 8: Check Status after entry
    status_1 = client.get("/api/status").json()
    assert status_1["occupiedSeats"] == 1
    assert status_1["availableSeats"] == 99

    # Step 9: Check Seats map after entry
    seats_1 = client.get("/api/seats", headers=headers).json()
    assert seats_1["occupiedCount"] == 1
    assert seats_1["availableCount"] == 99
    assert seats_1["mySeat"] == 1
    assert seats_1["nextAvailableSeat"] == 2
    assert seats_1["seats"][0]["status"] == "occupied"

    # Step 10: Check Current Visit (active)
    visit_1 = client.get("/api/visits/current", headers=headers).json()
    assert visit_1["active"] is True
    assert visit_1["visit"]["seatNumber"] == 1
    assert visit_1["visit"]["diningHall"] == "Central Mess"

    # Step 11: Exit Scan (Tray Return)
    exit_res = client.post(
        "/api/scan/exit",
        json={"scanType": "tray_return"},
        headers=headers,
    )
    assert exit_res.status_code == 200
    exit_data = exit_res.json()
    assert exit_data["success"] is True
    assert exit_data["visit"]["seatNumber"] == 1

    # Step 12: Check Status after exit
    status_2 = client.get("/api/status").json()
    assert status_2["occupiedSeats"] == 0
    assert status_2["availableSeats"] == 100

    # Step 13: Check Seats map after exit
    seats_2 = client.get("/api/seats", headers=headers).json()
    assert seats_2["occupiedCount"] == 0
    assert seats_2["availableCount"] == 100
    assert seats_2["mySeat"] is None
    assert seats_2["nextAvailableSeat"] == 1
    assert seats_2["seats"][0]["status"] == "available"

    # Step 14: Check Current Visit after exit
    visit_2 = client.get("/api/visits/current", headers=headers).json()
    assert visit_2["active"] is False
    assert visit_2["visit"] is None

    # Step 15: Check Visit History
    hist_res = client.get("/api/visits/history", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["pagination"]["total"] == 1
    assert hist_data["visits"][0]["seatNumber"] == 1
    assert hist_data["visits"][0]["status"] == "completed"
    assert hist_data["visits"][0]["exitReason"] == "tray_return"

    # Step 16: Check Notifications
    notif_res = client.get("/api/notifications", headers=headers)
    assert notif_res.status_code == 200
    notif_data = notif_res.json()
    assert notif_data["unreadCount"] == 1
    assert notif_data["pagination"]["total"] == 1
    assert notif_data["notifications"][0]["type"] == "visit"
    assert notif_data["notifications"][0]["title"] == "Visit completed"

    # Step 17: Mark Notification as Read
    notif_id = notif_data["notifications"][0]["id"]
    read_res = client.patch(f"/api/notifications/{notif_id}/read", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["success"] is True
    assert read_res.json()["notification"]["read"] is True

    notif_res_after = client.get("/api/notifications", headers=headers).json()
    assert notif_res_after["unreadCount"] == 0


# 2. Complete Timeout Lifecycle Journey
def test_e2e_timeout_lifecycle_journey(client: TestClient):
    """E2E Test 2: Automatic 25-minute seat timeout sweeper releases seat and updates history/notifications."""
    headers = _auth_header(TEST_STUDENT_ID)

    # Student enters
    entry_res = client.post("/api/scan/entry", json={"passCode": "PASS-8842"}, headers=headers)
    assert entry_res.status_code == 200
    assert client.get("/api/status").json()["occupiedSeats"] == 1

    # Artificially age the active visit to 30 minutes in the past
    past_entry = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    db_manager.occupancy.update_one(
        {"studentId": TEST_STUDENT_ID, "status": "occupied"},
        {"$set": {"entryTime": past_entry}},
    )

    # Run sweeper
    expired = expire_abandoned_visits()
    assert expired == 1

    # Verify status and seats freed
    assert client.get("/api/status").json()["occupiedSeats"] == 0
    seats_data = client.get("/api/seats", headers=headers).json()
    assert seats_data["occupiedCount"] == 0
    assert seats_data["mySeat"] is None
    assert seats_data["nextAvailableSeat"] == 1

    # Verify active visit is none
    assert client.get("/api/visits/current", headers=headers).json()["active"] is False

    # Verify visit history shows expired
    hist_data = client.get("/api/visits/history", headers=headers).json()
    assert hist_data["pagination"]["total"] == 1
    assert hist_data["visits"][0]["status"] == "expired"
    assert hist_data["visits"][0]["exitReason"] == "timeout"

    # Verify notification received
    notif_data = client.get("/api/notifications", headers=headers).json()
    assert notif_data["pagination"]["total"] == 1
    assert notif_data["notifications"][0]["type"] == "visit"
    assert notif_data["notifications"][0]["title"] == "Visit timed out"


# 3. 60-Student Crowd Rush Demo Flow
def test_e2e_60_students_crowd_rush_demo_flow(client: TestClient):
    """E2E Test 3: Simulate 60 students entering mess, reaching 60% Moderate Crowd, and 1 student tray return."""
    # 1. Simulate 60 students entering
    now_iso = datetime.now(timezone.utc).isoformat()
    occupancy_docs = [
        {
            "studentId": f"STU_SIM_{i}",
            "seatNumber": i,
            "diningHall": "Central Mess",
            "entryTime": now_iso,
            "exitTime": None,
            "status": "occupied",
            "mealType": "Lunch",
        }
        for i in range(1, 61)
    ]
    # Set student 24 to TEST_STUDENT_ID
    occupancy_docs[23]["studentId"] = TEST_STUDENT_ID
    db_manager.occupancy.insert_many(occupancy_docs)

    # 2. Check live status: 60 occupied, 40 available, 60%, Moderate Crowd
    status_data = client.get("/api/status").json()
    assert status_data["totalSeats"] == 100
    assert status_data["occupiedSeats"] == 60
    assert status_data["availableSeats"] == 40
    assert status_data["occupancyPercentage"] == 60
    assert status_data["crowdLevel"] == "Moderate"

    # 3. Check Find a Seat map
    seats_data = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID)).json()
    assert seats_data["capacity"] == 100
    assert seats_data["occupiedCount"] == 60
    assert seats_data["availableCount"] == 40
    assert seats_data["mySeat"] == 24
    assert seats_data["nextAvailableSeat"] == 61

    # 4. Student 24 performs tray return
    exit_res = client.post("/api/scan/exit", json={"scanType": "tray_return"}, headers=_auth_header(TEST_STUDENT_ID))
    assert exit_res.status_code == 200

    # 5. Status becomes 59 occupied, 41 available
    status_after = client.get("/api/status").json()
    assert status_after["occupiedSeats"] == 59
    assert status_after["availableSeats"] == 41
    assert status_after["occupancyPercentage"] == 59
    assert status_after["crowdLevel"] == "Moderate"

    # 6. Seat 24 is now the lowest available seat
    seats_after = client.get("/api/seats", headers=_auth_header(TEST_STUDENT_ID)).json()
    assert seats_after["occupiedCount"] == 59
    assert seats_after["availableCount"] == 41
    assert seats_after["nextAvailableSeat"] == 24
    assert seats_after["mySeat"] is None


# 4. Crowd Threshold Boundaries
def test_e2e_crowd_threshold_boundaries(client: TestClient):
    """E2E Test 4: Verify boundary conditions: 0 (Low), 49 (Low), 50 (Moderate), 80 (Moderate), 81 (Peak Rush), 100 (Peak Rush)."""
    now_iso = datetime.now(timezone.utc).isoformat()

    def _set_occupancy(count: int):
        db_manager.occupancy.delete_many({})
        if count > 0:
            db_manager.occupancy.insert_many([
                {
                    "studentId": f"STU_{i}",
                    "seatNumber": i,
                    "diningHall": "Central Mess",
                    "entryTime": now_iso,
                    "exitTime": None,
                    "status": "occupied",
                }
                for i in range(1, count + 1)
            ])

    # 0 -> 0% -> Low
    _set_occupancy(0)
    res0 = client.get("/api/status").json()
    assert res0["occupancyPercentage"] == 0
    assert res0["crowdLevel"] == "Low"

    # 49 -> 49% -> Low
    _set_occupancy(49)
    res49 = client.get("/api/status").json()
    assert res49["occupancyPercentage"] == 49
    assert res49["crowdLevel"] == "Low"

    # 50 -> 50% -> Moderate
    _set_occupancy(50)
    res50 = client.get("/api/status").json()
    assert res50["occupancyPercentage"] == 50
    assert res50["crowdLevel"] == "Moderate"

    # 80 -> 80% -> Moderate
    _set_occupancy(80)
    res80 = client.get("/api/status").json()
    assert res80["occupancyPercentage"] == 80
    assert res80["crowdLevel"] == "Moderate"

    # 81 -> 81% -> Peak Rush
    _set_occupancy(81)
    res81 = client.get("/api/status").json()
    assert res81["occupancyPercentage"] == 81
    assert res81["crowdLevel"] == "Peak Rush"

    # 100 -> 100% -> Peak Rush
    _set_occupancy(100)
    res100 = client.get("/api/status").json()
    assert res100["occupancyPercentage"] == 100
    assert res100["crowdLevel"] == "Peak Rush"


# 5. Full Capacity Rejection and Seat Reuse
def test_e2e_full_capacity_rejection_and_seat_reuse(client: TestClient):
    """E2E Test 5: At 100/100 full capacity, 101st entry is rejected with 409; freeing a seat enables reuse."""
    now_iso = datetime.now(timezone.utc).isoformat()
    # Fill 100 seats
    all_100 = [
        {
            "studentId": f"STU_{i}",
            "seatNumber": i,
            "diningHall": "Central Mess",
            "entryTime": now_iso,
            "exitTime": None,
            "status": "occupied",
        }
        for i in range(1, 101)
    ]
    db_manager.occupancy.insert_many(all_100)

    # 101st entry attempt for TEST_STUDENT_ID fails with 409
    entry_res = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8842"},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert entry_res.status_code == 409
    assert "No seats are currently available" in entry_res.json()["detail"]

    # Free seat 15
    db_manager.occupancy.update_one(
        {"seatNumber": 15},
        {"$set": {"status": "completed", "exitTime": now_iso}},
    )

    # Now entry succeeds and assigns seat 15
    retry_res = client.post(
        "/api/scan/entry",
        json={"passCode": "PASS-8842"},
        headers=_auth_header(TEST_STUDENT_ID),
    )
    assert retry_res.status_code == 200
    assert retry_res.json()["seatNumber"] == 15


# 6. Duplicate Active Visit Protection
def test_e2e_duplicate_entry_attempt_rejected(client: TestClient):
    """E2E Test 6: Student cannot check in twice simultaneously."""
    headers = _auth_header(TEST_STUDENT_ID)

    # First check-in succeeds
    first_res = client.post("/api/scan/entry", json={"passCode": "PASS-8842"}, headers=headers)
    assert first_res.status_code == 200

    # Immediate second check-in fails with 409
    second_res = client.post("/api/scan/entry", json={"passCode": "PASS-8842"}, headers=headers)
    assert second_res.status_code == 409
    assert "already have an active dining visit" in second_res.json()["detail"]

    # Exactly 1 active record exists
    active_count = db_manager.occupancy.count_documents({"studentId": TEST_STUDENT_ID, "status": "occupied"})
    assert active_count == 1


# 7. Concurrent Exit and Timeout Race Safety
def test_e2e_concurrent_exit_and_timeout_race(client: TestClient):
    """E2E Test 7: Race between tray return and timeout sweeper transitions visit exactly once."""
    now_iso = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    db_manager.occupancy.insert_one({
        "studentId": TEST_STUDENT_ID,
        "seatNumber": 10,
        "diningHall": "Central Mess",
        "entryTime": now_iso,
        "exitTime": None,
        "status": "occupied",
    })

    # Trigger exit scan
    exit_details = complete_current_visit(TEST_STUDENT_ID)
    assert exit_details is not None

    # Immediate sweeper run on the same visit
    expired_count = expire_abandoned_visits()
    assert expired_count == 0  # Sweeper found 0 matching active visits because it was already completed!

    # Final document state is completed
    doc = db_manager.occupancy.find_one({"studentId": TEST_STUDENT_ID})
    assert doc["status"] == "completed"
    assert doc["exitReason"] == "tray_return"

    # Exactly 1 notification created
    notifs = list(db_manager.notifications.find({"studentId": TEST_STUDENT_ID}))
    assert len(notifs) == 1
    assert notifs[0]["title"] == "Visit completed"


# 8. Settings & Notification Preferences Flow
def test_e2e_settings_password_and_notification_toggle_flow(client: TestClient):
    """E2E Test 8: Settings preference toggle suppresses notifications; password change updates credentials."""
    headers = _auth_header(TEST_STUDENT_ID)

    # 1. Disable notifications in settings
    patch_prefs = client.patch("/api/settings", json={"notificationsEnabled": False}, headers=headers)
    assert patch_prefs.status_code == 200
    assert patch_prefs.json()["preferences"]["notificationsEnabled"] is False

    # 2. Enter and exit mess
    client.post("/api/scan/entry", json={"passCode": "PASS-8842"}, headers=headers)
    client.post("/api/scan/exit", json={"scanType": "tray_return"}, headers=headers)

    # 3. Verify NO notification was created because preferences disabled notifications
    notifs = client.get("/api/notifications", headers=headers).json()
    assert notifs["pagination"]["total"] == 0

    # 4. Change password in settings
    new_pwd = "NewSecurePassword2026!"
    pwd_res = client.patch(
        "/api/settings/password",
        json={"currentPassword": TEST_PASSWORD, "newPassword": new_pwd},
        headers=headers,
    )
    assert pwd_res.status_code == 200

    # 5. Verify old password fails login
    assert client.post("/api/auth/login", json={"studentId": TEST_STUDENT_ID, "password": TEST_PASSWORD}).status_code == 401

    # 6. Verify new password succeeds login
    login_new = client.post("/api/auth/login", json={"studentId": TEST_STUDENT_ID, "password": new_pwd})
    assert login_new.status_code == 200
    assert "accessToken" in login_new.json()


# 9. Polling Safety (No writes or notifications on read endpoints)
def test_e2e_polling_safety(client: TestClient):
    """E2E Test 9: Rapid polling of /api/status and /api/seats does not mutate database or create notifications."""
    headers = _auth_header(TEST_STUDENT_ID)

    # Poll status and seats 10 times each
    for _ in range(10):
        status_res = client.get("/api/status")
        assert status_res.status_code == 200
        seats_res = client.get("/api/seats", headers=headers)
        assert seats_res.status_code == 200

    # Total notifications remains 0
    assert db_manager.notifications.count_documents({}) == 0
    assert db_manager.occupancy.count_documents({}) == 0


# 10. Seed Scripts Idempotency
def test_e2e_seed_scripts_idempotency():
    """E2E Test 10: Calling seed functions repeatedly does not duplicate students or menu items."""
    # Seed students twice
    seed_students_fn()
    count1 = db_manager.students.count_documents({})
    seed_students_fn()
    count2 = db_manager.students.count_documents({})
    assert count1 == count2
    assert count1 >= 4

    # Seed menu twice
    seed_menu_fn("2026-09-12")
    menu_count1 = db_manager.menu.count_documents({"date": "2026-09-12"})
    seed_menu_fn("2026-09-12")
    menu_count2 = db_manager.menu.count_documents({"date": "2026-09-12"})
    assert menu_count1 == menu_count2
    assert menu_count1 == 2  # Lunch and Dinner
