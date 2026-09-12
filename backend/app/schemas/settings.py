from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.auth import StudentPublic


class StudentPreferences(BaseModel):
    """Schema representing user-configurable application preferences."""

    model_config = ConfigDict(extra="forbid")

    notificationsEnabled: bool = Field(
        default=True,
        description="Whether notifications are enabled for the student",
    )


class UpdateSettingsRequest(BaseModel):
    """Schema for updating student settings/preferences.

    Strictly whitelists allowed preference updates and forbids arbitrary fields.
    """

    model_config = ConfigDict(extra="forbid")

    notificationsEnabled: Optional[bool] = Field(
        default=None,
        description="Toggle notification delivery on or off",
    )
    preferences: Optional[StudentPreferences] = Field(
        default=None,
        description="Optional nested preferences object",
    )


class SettingsResponse(BaseModel):
    """Schema for settings information returned to the student."""

    student: StudentPublic = Field(..., description="Student profile details (ID, name)")
    diningHall: str = Field(..., description="Assigned or default campus dining hall")
    preferences: StudentPreferences = Field(..., description="Current application preferences")


class ChangePasswordRequest(BaseModel):
    """Schema for changing the student's account password."""

    model_config = ConfigDict(extra="forbid")

    currentPassword: str = Field(..., min_length=1, description="Current student password")
    newPassword: str = Field(..., min_length=1, description="New student password")


class ChangePasswordResponse(BaseModel):
    """Schema returned after a successful password change."""

    success: bool = Field(default=True, description="Indicates operation success")
    message: str = Field(default="Password changed successfully.", description="Status message")
