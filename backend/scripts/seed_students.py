"""Seed script to populate demo students into MongoDB.

DEMO CREDENTIALS (LOCAL DEVELOPMENT / DEMO TESTING ONLY):
---------------------------------------------------------
1. Student ID: STU1042 | Password: DineSpace2026! | Name: Sarah Chen   | Active: True
2. Student ID: STU1043 | Password: DineSpace2026! | Name: Alex Sharma  | Active: True
3. Student ID: STU1044 | Password: DineSpace2026! | Name: Rahul Singh  | Active: True
4. Student ID: STU9999 | Password: DineSpace2026! | Name: Inactive User| Active: False
"""

import logging
import sys
from pymongo.errors import PyMongoError

from app.database import db_manager
from app.services.security import hash_password

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_students")

# DEMO PASSWORD FOR LOCAL TESTING ONLY
DEMO_PASSWORD = "DineSpace2026!"

DEMO_STUDENTS = [
    {
        "studentId": "STU1042",
        "name": "Sarah Chen",
        "passCode": "PASS-8842",
        "isActive": True,
    },
    {
        "studentId": "STU1043",
        "name": "Alex Sharma",
        "passCode": "PASS-8843",
        "isActive": True,
    },
    {
        "studentId": "STU1044",
        "name": "Rahul Singh",
        "passCode": "PASS-8844",
        "isActive": True,
    },
    {
        "studentId": "STU9999",
        "name": "Inactive Student",
        "passCode": "PASS-9999",
        "isActive": False,
    },
]


def seed() -> None:
    """Seed demo students into MongoDB with bcrypt-hashed passwords."""
    logger.info("Connecting to MongoDB...")
    db_manager.connect()

    if not db_manager.ping():
        logger.error(
            "Cannot connect to MongoDB. Please ensure MongoDB is running or configure MONGODB_URI."
        )
        sys.exit(1)

    students_col = db_manager.students

    # Ensure unique index on studentId
    try:
        students_col.create_index("studentId", unique=True)
        logger.info("Ensured unique index on studentId.")
    except PyMongoError as exc:
        logger.warning("Failed to create index on studentId: %s", exc)

    logger.info("Generating password hashes and seeding %d demo students...", len(DEMO_STUDENTS))
    password_hash = hash_password(DEMO_PASSWORD)

    for student in DEMO_STUDENTS:
        record = {
            "studentId": student["studentId"],
            "name": student["name"],
            "passCode": student["passCode"],
            "passwordHash": password_hash,
            "isActive": student["isActive"],
        }
        students_col.update_one(
            {"studentId": student["studentId"]},
            {"$set": record},
            upsert=True,
        )
        logger.info(
            "Seeded student: %s (%s) [Active: %s]",
            student["studentId"],
            student["name"],
            student["isActive"],
        )

    logger.info("Demo student seeding completed successfully.")
    logger.info("Demo credentials password: %s", DEMO_PASSWORD)


if __name__ == "__main__":
    seed()
