import logging
from typing import Any, Dict

from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from app.config import get_settings
from app.database import db_manager
from app.schemas.auth import StudentPublic
from app.schemas.settings import (
    ChangePasswordResponse,
    SettingsResponse,
    StudentPreferences,
    UpdateSettingsRequest,
)
from app.services.security import hash_password, verify_password

logger = logging.getLogger(__name__)


def get_student_settings(student_id: str) -> SettingsResponse:
    """Retrieve settings and preferences for the authenticated student.

    Args:
        student_id: Unique student identification string.

    Returns:
        SettingsResponse containing profile details, default dining hall, and preferences.

    Raises:
        HTTPException(404): If the student record is not found.
        HTTPException(500): If database access fails.
    """
    settings = get_settings()
    try:
        student = db_manager.students.find_one(
            {"studentId": student_id},
            projection={"studentId": 1, "name": 1, "preferences": 1, "isActive": 1, "_id": 0},
        )
    except PyMongoError as exc:
        logger.error("Database query failed while fetching settings for %s: %s", student_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error retrieving student settings.",
        )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student account not found.",
        )

    preferences_dict = student.get("preferences") or {}
    notifications_enabled = preferences_dict.get("notificationsEnabled", True)

    return SettingsResponse(
        student=StudentPublic(
            studentId=student["studentId"],
            name=student["name"],
        ),
        diningHall=settings.DEFAULT_DINING_HALL,
        preferences=StudentPreferences(
            notificationsEnabled=bool(notifications_enabled),
        ),
    )


def update_student_settings(
    student_id: str,
    payload: UpdateSettingsRequest,
) -> SettingsResponse:
    """Update supported preferences for the authenticated student using targeted $set.

    Prevents arbitrary field modification by only whitelisting supported preference fields.

    Args:
        student_id: Unique student identification string.
        payload: Validated update payload.

    Returns:
        Updated SettingsResponse.

    Raises:
        HTTPException(404): If student does not exist.
        HTTPException(500): If database update fails.
    """
    # Resolve requested notificationsEnabled value if provided
    new_notif_enabled = None
    if payload.notificationsEnabled is not None:
        new_notif_enabled = payload.notificationsEnabled
    elif payload.preferences and payload.preferences.notificationsEnabled is not None:
        new_notif_enabled = payload.preferences.notificationsEnabled

    if new_notif_enabled is not None:
        try:
            result = db_manager.students.update_one(
                {"studentId": student_id},
                {"$set": {"preferences.notificationsEnabled": new_notif_enabled}},
            )
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student account not found.",
                )
            logger.info(
                "Updated preferences.notificationsEnabled to %s for student %s",
                new_notif_enabled,
                student_id,
            )
        except PyMongoError as exc:
            logger.error("Database update failed while updating settings for %s: %s", student_id, exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error updating student settings.",
            )

    return get_student_settings(student_id)


def change_student_password(
    student_id: str,
    current_password: str,
    new_password: str,
) -> ChangePasswordResponse:
    """Verify existing password and securely update to a new bcrypt-hashed password.

    Args:
        student_id: Unique student identification string.
        current_password: The student's current plaintext password.
        new_password: The desired new plaintext password.

    Returns:
        ChangePasswordResponse confirming success.

    Raises:
        HTTPException(400): If current password is incorrect or empty.
        HTTPException(404): If student account is not found.
        HTTPException(500): If database update fails.
    """
    try:
        student = db_manager.students.find_one({"studentId": student_id})
    except PyMongoError as exc:
        logger.error("Database query failed while changing password for %s: %s", student_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error processing password change.",
        )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student account not found.",
        )

    # Verify current password
    stored_hash = student.get("passwordHash", "")
    if not verify_password(current_password, stored_hash):
        logger.warning("Password change failed for student %s: incorrect current password", student_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    # Hash new password
    new_hash = hash_password(new_password)

    # Atomically update passwordHash
    try:
        db_manager.students.update_one(
            {"studentId": student_id},
            {"$set": {"passwordHash": new_hash}},
        )
        logger.info("Successfully updated passwordHash for student %s", student_id)
    except PyMongoError as exc:
        logger.error("Database error updating passwordHash for %s: %s", student_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error updating student password.",
        )

    return ChangePasswordResponse(
        success=True,
        message="Password changed successfully.",
    )
