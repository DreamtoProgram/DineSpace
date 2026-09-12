import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from app.database import db_manager
from app.services.security import verify_password

logger = logging.getLogger(__name__)


def ensure_student_indexes() -> None:
    """Ensure unique index on studentId exists in MongoDB students collection."""
    try:
        db_manager.students.create_index("studentId", unique=True)
        logger.info("Ensured unique index on students.studentId")
    except PyMongoError as exc:
        logger.warning("Could not ensure index on students.studentId: %s", exc)


def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a student record by studentId from MongoDB.

    Args:
        student_id: The unique identifier of the student (e.g. STU1042).

    Returns:
        Student document dictionary if found, None otherwise.
    """
    try:
        return db_manager.students.find_one({"studentId": student_id})
    except PyMongoError as exc:
        logger.error("Database query failed while fetching student %s: %s", student_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database service temporarily unavailable.",
        )


def authenticate_student(student_id: str, password: str) -> Dict[str, Any]:
    """Validate student credentials and return the student record if authentic.

    Args:
        student_id: The student identifier.
        password: The plaintext password provided.

    Returns:
        The authenticated student record.

    Raises:
        HTTPException(401): If student does not exist or password is invalid.
        HTTPException(403): If student exists but account is inactive.
    """
    student = get_student_by_id(student_id)

    # 1. Student does not exist
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid student ID or password",
        )

    # 2. Student is inactive
    if not student.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student account is inactive. Please contact dining hall administration.",
        )

    # 3. Incorrect password
    stored_hash = student.get("passwordHash", "")
    if not verify_password(password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid student ID or password",
        )

    return student
