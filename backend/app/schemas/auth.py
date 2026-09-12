from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema for student login request."""

    studentId: str = Field(..., min_length=1, description="Student ID (e.g. STU1042)")
    password: str = Field(..., min_length=1, description="Student account password")


class StudentPublic(BaseModel):
    """Public profile schema of an authenticated student (safe for client responses)."""

    studentId: str = Field(..., description="Unique student ID")
    name: str = Field(..., description="Student's full name")


class LoginResponse(BaseModel):
    """Schema for successful authentication response."""

    success: bool = Field(default=True, description="Indicates if the operation succeeded")
    message: str = Field(default="Login successful", description="Status message")
    accessToken: str = Field(..., description="JWT bearer access token")
    tokenType: str = Field(default="bearer", description="Token authentication scheme")
    student: StudentPublic = Field(..., description="Public profile of authenticated student")
