from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.auth import StudentPublic


class EntryScanRequest(BaseModel):
    """Request schema for student dining hall QR entry scan."""

    passCode: str = Field(..., min_length=1, description="Scanned pass code (e.g. PASS-8842)")
    diningHall: Optional[str] = Field(
        default=None,
        description="Optional target dining hall name. Defaults to system default if omitted.",
    )


class EntrySuccessResponse(BaseModel):
    """Response schema upon successful dining hall entry and seat assignment."""

    success: bool = Field(default=True, description="Indicates operation success")
    message: str = Field(default="Entry successful", description="Status message")
    student: StudentPublic = Field(..., description="Public profile of student checked in")
    seatNumber: int = Field(..., description="Assigned lowest available virtual seat number (1 to TOTAL_SEATS)")
    diningHall: str = Field(..., description="Dining hall facility where seat is assigned")
    entryTime: str = Field(..., description="Timezone-aware ISO 8601 timestamp of check-in")
    mealType: Optional[str] = Field(default=None, description="Current meal category (e.g. Lunch, Dinner)")


class ExitScanRequest(BaseModel):
    """Request schema for dining hall tray return / exit scan."""

    scanType: Optional[str] = Field(
        default="tray_return",
        description="Type of exit scan operation (must be 'tray_return' if provided)",
    )


class CompletedVisitDetails(BaseModel):
    """Summary of a completed dining visit."""

    seatNumber: int = Field(..., description="Virtual seat number that was occupied")
    diningHall: str = Field(..., description="Dining hall facility name")
    entryTime: str = Field(..., description="Timezone-aware ISO 8601 entry timestamp")
    exitTime: str = Field(..., description="Timezone-aware ISO 8601 exit timestamp")
    durationMinutes: int = Field(..., description="Total dining duration in whole minutes")
    mealType: Optional[str] = Field(default=None, description="Meal category for this visit")


class ExitSuccessResponse(BaseModel):
    """Response schema upon successful visit completion and seat release."""

    success: bool = Field(default=True, description="Indicates operation success")
    message: str = Field(default="Visit completed successfully", description="Status message")
    visit: CompletedVisitDetails = Field(..., description="Summary details of the completed visit")

