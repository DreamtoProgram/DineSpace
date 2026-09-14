"""Seed script to populate sample notifications into MongoDB."""

import logging
from datetime import datetime, timezone
from app.database import db_manager
from app.services.notification_service import ensure_notification_indexes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_notifications")

SAMPLE_NOTIFICATIONS = [
    {
        "type": "crowd",
        "title": "Low Crowd Alert",
        "message": "Central Mess occupancy is currently at 37%. Perfect time to enjoy your meal without waiting!",
        "read": False,
        "createdAt": datetime.now(timezone.utc),
    },
    {
        "type": "menu",
        "title": "Special Lunch Menu Today",
        "message": "Chef Special Paneer Butter Masala, Dal Makhani, and hot Gulab Jamuns are now being served.",
        "read": False,
        "createdAt": datetime.now(timezone.utc),
    },
    {
        "type": "visit",
        "title": "Tray Return Recorded",
        "message": "Thank you for clearing your tray at Station 2! Seat #24 has been freed.",
        "read": True,
        "createdAt": datetime.now(timezone.utc),
    },
    {
        "type": "system",
        "title": "Semester Pass Active",
        "message": "Your unlimited campus resident dining pass for Semester II is fully active.",
        "read": True,
        "createdAt": datetime.now(timezone.utc),
    },
]

def seed() -> None:
    db_manager.connect()
    if not db_manager.ping():
        logger.error("Cannot connect to MongoDB.")
        return

    ensure_notification_indexes()
    notif_col = db_manager.notifications

    for student_id in ["STU1042", "P132-NNK"]:
        for item in SAMPLE_NOTIFICATIONS:
            doc = {
                "studentId": student_id,
                "type": item["type"],
                "title": item["title"],
                "message": item["message"],
                "read": item["read"],
                "createdAt": item["createdAt"],
            }
            notif_col.update_one(
                {"studentId": student_id, "title": item["title"]},
                {"$set": doc},
                upsert=True,
            )
        logger.info("Seeded sample notifications for student: %s", student_id)

    logger.info("Notifications seeding completed.")

if __name__ == "__main__":
    seed()
