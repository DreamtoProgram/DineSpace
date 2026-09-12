from typing import Any, Dict
from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_student
from app.schemas.settings import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    SettingsResponse,
    UpdateSettingsRequest,
)
from app.services.settings_service import (
    change_student_password,
    get_student_settings,
    update_student_settings,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student Settings and Preferences",
    description=(
        "Retrieve account profile details (Student ID, name), campus dining hall, and "
        "configurable application preferences for the authenticated student."
    ),
    responses={
        200: {"description": "Settings successfully retrieved."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
        404: {"description": "Student account not found."},
    },
)
def get_settings(
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> SettingsResponse:
    """Return the authenticated student's profile and preferences."""
    student_id = current_student["studentId"]
    return get_student_settings(student_id)


@router.patch(
    "",
    response_model=SettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Student Preferences",
    description=(
        "Update supported student preferences (e.g. notificationsEnabled). "
        "Arbitrary field updates are strictly forbidden to ensure schema and data safety."
    ),
    responses={
        200: {"description": "Settings successfully updated."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
        404: {"description": "Student account not found."},
        422: {"description": "Validation error on submitted preferences or unknown fields."},
    },
)
def update_settings(
    payload: UpdateSettingsRequest,
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> SettingsResponse:
    """Update whitelisted preferences for the authenticated student."""
    student_id = current_student["studentId"]
    return update_student_settings(student_id=student_id, payload=payload)


@router.patch(
    "/password",
    response_model=ChangePasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Change Student Password",
    description=(
        "Securely change the student's account password. Verifies current password against "
        "stored bcrypt hash before persisting the newly hashed password. Never exposes hashes or plaintext."
    ),
    responses={
        200: {"description": "Password changed successfully."},
        400: {"description": "Current password is incorrect."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
        404: {"description": "Student account not found."},
        422: {"description": "Validation error (e.g. empty or missing password field)."},
    },
)
def change_password(
    payload: ChangePasswordRequest,
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> ChangePasswordResponse:
    """Validate current password and update to new bcrypt-hashed password."""
    student_id = current_student["studentId"]
    return change_student_password(
        student_id=student_id,
        current_password=payload.currentPassword,
        new_password=payload.newPassword,
    )
