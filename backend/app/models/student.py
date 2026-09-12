from pydantic import BaseModel, Field


class Student(BaseModel):
    """Internal domain model representing a student record in MongoDB."""

    studentId: str = Field(..., description="Unique student identification number (e.g. STU1042)")
    name: str = Field(..., description="Student's full name")
    passCode: str = Field(..., description="Unique dining hall entry pass code (e.g. PASS-8842)")
    passwordHash: str = Field(..., description="Secure bcrypt hash of the student password")
    isActive: bool = Field(default=True, description="Whether the student account is active for login")
