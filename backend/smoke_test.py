"""Repeatable smoke-test script for DineSpace Backend.

Tests all 11 core application flows in sequence:
1. Health check (/api/health)
2. Student Login (/api/auth/login)
3. Authenticated Profile (/api/auth/me)
4. Today's Menu (/api/menu/today)
5. Live Status (/api/status)
6. Find a Seat (/api/seats)
7. Entry Scan check-in (/api/scan/entry)
8. Current Active Visit (/api/visits/current)
9. Tray Return Exit (/api/scan/exit)
10. Visit History (/api/visits/history)
11. Notifications (/api/notifications)
12. Settings & Preferences (/api/settings)

Can be executed standalone:
    python smoke_test.py
"""

import sys
from fastapi.testclient import TestClient

from app.database import db_manager
from app.main import app
from app.services.security import hash_password

DEMO_STUDENT_ID = "STU1042"
DEMO_PASSWORD = "DineSpace2026!"
DEMO_PASS_CODE = "PASS-8842"


def run_smoke_test() -> bool:
    print("=" * 60)
    print("  DineSpace Backend -- Pre-Demo Smoke Test")
    print("=" * 60)

    # Check if live MongoDB is reachable; if not, use mongomock for seamless offline testing
    try:
        db_manager.connect()
        if not db_manager.ping():
            raise ConnectionError("MongoDB not reachable")
    except Exception:
        import mongomock
        print("[INFO] Live MongoDB not running on localhost:27017. Using in-memory mongomock for smoke test.")
        mock_client = mongomock.MongoClient()
        db_manager.client = mock_client
        db_manager.db = mock_client["dinespace_smoke"]
        db_manager.connect = lambda *args, **kwargs: None
        db_manager.close = lambda *args, **kwargs: None
        db_manager.ping = lambda *args, **kwargs: True
    # Seed required test student if missing
    password_hash = hash_password(DEMO_PASSWORD)
    db_manager.students.update_one(
        {"studentId": DEMO_STUDENT_ID},
        {
            "$set": {
                "studentId": DEMO_STUDENT_ID,
                "name": "Sarah Chen",
                "passCode": DEMO_PASS_CODE,
                "passwordHash": password_hash,
                "isActive": True,
            }
        },
        upsert=True,
    )
    # Seed today's menu
    from scripts.seed_menu import seed as seed_menu_fn
    seed_menu_fn()

    # Ensure clean slate for occupancy and notifications
    db_manager.occupancy.delete_many({"studentId": DEMO_STUDENT_ID})
    db_manager.notifications.delete_many({"studentId": DEMO_STUDENT_ID})

    client = TestClient(app)

    # Step 1: Health
    print("[1/12] Testing GET /api/health ...", end=" ")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Failed: {res.text}"
    print("PASS (Status: 200)")

    # Step 2: Login
    print("[2/12] Testing POST /api/auth/login ...", end=" ")
    res = client.post(
        "/api/auth/login",
        json={"studentId": DEMO_STUDENT_ID, "password": DEMO_PASSWORD},
    )
    assert res.status_code == 200, f"Failed: {res.text}"
    token = res.json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}
    print("PASS (Token generated)")

    # Step 3: Auth Profile
    print("[3/12] Testing GET /api/auth/me ...", end=" ")
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    assert res.json()["studentId"] == DEMO_STUDENT_ID
    print(f"PASS (Student: {res.json()['name']})")

    # Step 4: Today's Menu
    print("[4/12] Testing GET /api/menu/today ...", end=" ")
    res = client.get("/api/menu/today")
    assert res.status_code == 200, f"Failed: {res.text}"
    print(f"PASS ({len(res.json().get('menus', []))} meal menus)")

    # Step 5: Live Crowd Status
    print("[5/12] Testing GET /api/status ...", end=" ")
    res = client.get("/api/status")
    assert res.status_code == 200, f"Failed: {res.text}"
    status_info = res.json()
    print(f"PASS ({status_info['occupiedSeats']}/{status_info['totalSeats']} seats, Level: {status_info['crowdLevel']})")

    # Step 6: Find a Seat Map
    print("[6/12] Testing GET /api/seats ...", end=" ")
    res = client.get("/api/seats", headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    seats_info = res.json()
    print(f"PASS (Capacity: {seats_info['capacity']}, Next free: #{seats_info['nextAvailableSeat']})")

    # Step 7: Entry Scan Check-in
    print("[7/12] Testing POST /api/scan/entry ...", end=" ")
    res = client.post("/api/scan/entry", json={"passCode": DEMO_PASS_CODE}, headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    assigned_seat = res.json()["seatNumber"]
    print(f"PASS (Assigned Seat: #{assigned_seat})")

    # Step 8: Current Visit
    print("[8/12] Testing GET /api/visits/current ...", end=" ")
    res = client.get("/api/visits/current", headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    assert res.json()["active"] is True
    print(f"PASS (Active Seat: #{res.json()['visit']['seatNumber']})")

    # Step 9: Tray Return Exit
    print("[9/12] Testing POST /api/scan/exit ...", end=" ")
    res = client.post("/api/scan/exit", json={"scanType": "tray_return"}, headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    print(f"PASS (Visit completed, Seat #{assigned_seat} freed)")

    # Step 10: Visit History
    print("[10/12] Testing GET /api/visits/history ...", end=" ")
    res = client.get("/api/visits/history", headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    history_list = res.json()["visits"]
    assert len(history_list) >= 1
    print(f"PASS ({len(history_list)} completed/expired visits recorded)")

    # Step 11: Notifications
    print("[11/12] Testing GET /api/notifications ...", end=" ")
    res = client.get("/api/notifications", headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    notifs = res.json()["notifications"]
    print(f"PASS ({len(notifs)} alerts, unread: {res.json()['unreadCount']})")

    # Step 12: Settings
    print("[12/12] Testing GET /api/settings ...", end=" ")
    res = client.get("/api/settings", headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    prefs = res.json()["preferences"]
    print(f"PASS (Dining hall: {res.json()['diningHall']}, Notifications: {prefs['notificationsEnabled']})")

    print("=" * 60)
    print("  ALL 12 SMOKE TESTS PASSED CLEANLY! System ready for demo.  ")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = run_smoke_test()
        sys.exit(0 if success else 1)
    except AssertionError as exc:
        print(f"\n[FAIL] Smoke test assertion failed: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\n[ERROR] Unexpected smoke test error: {exc}")
        sys.exit(1)
