from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema for student login request."""

    studentId: str = Field(..., min_length=1, description="Student ID (e.g. STU1042)")
    password: str = Field(..., min_length=1, description="Student account password")


class StudentPublic(BaseModel):
    """Public profile schema of an authenticated student (safe for client responses)."""

    studentId: str = Field(..., description="Unique student ID")
    name: str = Field(..., description="Student's full name")
    role: str = Field(default="student", description="Account role: 'student' or 'admin'")
    department: Optional[str] = Field(default=None, description="Department or staff unit")
    email: Optional[str] = Field(default=None, description="University email address")
    rfidCardUid: Optional[str] = Field(default=None, description="Physical RFID badge serial number")
    ssoProvider: Optional[str] = Field(default=None, description="SSO authentication provider")


class SSOLoginRequest(BaseModel):
    """Schema for campus Single Sign-On (Google / Microsoft 365 / Campus ERP)."""

    provider: str = Field(..., description="SSO Provider: 'google', 'microsoft', or 'campus_erp'")
    token: Optional[str] = Field(default=None, description="OAuth2 ID token or authorization token")
    email: Optional[str] = Field(default=None, description="Verified institutional student email")
    name: Optional[str] = Field(default=None, description="Student full name from directory")


class RFIDTapRequest(BaseModel):
    """Schema for tapping an RFID/NFC smart student badge."""

    cardUid: str = Field(..., min_length=1, description="Unique physical RFID/NFC chip serial or card identifier")
    diningHall: Optional[str] = Field(default="Central Mess", description="Target dining hall")


class LoginResponse(BaseModel):
    """Schema for successful authentication response."""

    success: bool = Field(default=True, description="Indicates if the operation succeeded")
    message: str = Field(default="Login successful", description="Status message")
    accessToken: str = Field(..., description="JWT bearer access token")
    tokenType: str = Field(default="bearer", description="Token authentication scheme")
    student: StudentPublic = Field(..., description="Public profile of authenticated student")
