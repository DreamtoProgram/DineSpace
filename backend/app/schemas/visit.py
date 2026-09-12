from typing import List, Optional
from pydantic import BaseModel, Field


class ActiveVisitDetails(BaseModel):
    """Details of an active dining session."""

    seatNumber: int = Field(..., description="Assigned virtual seat number")
    diningHall: str = Field(..., description="Dining hall facility name")
    entryTime: str = Field(..., description="Timezone-aware ISO 8601 entry timestamp")
    durationMinutes: int = Field(..., description="Elapsed dining duration in whole minutes")
    mealType: Optional[str] = Field(default=None, description="Meal category for this visit")


class CurrentVisitResponse(BaseModel):
    """Response schema for retrieving current active dining visit."""

    active: bool = Field(..., description="Whether the student has an ongoing dining session")
    visit: Optional[ActiveVisitDetails] = Field(
        default=None,
        description="Active visit details if active=True, otherwise null",
    )


class PaginationDetails(BaseModel):
    """Pagination metadata for paginated collection responses."""

    limit: int = Field(..., description="Number of items returned per page")
    offset: int = Field(..., description="Offset number of records skipped")
    total: int = Field(..., description="Total count of matching records across all pages")


class VisitHistoryItem(BaseModel):
    """Details of a single past dining visit (completed or expired)."""

    seatNumber: int = Field(..., description="Virtual seat number occupied during this visit")
    diningHall: str = Field(..., description="Dining hall facility name")
    mealType: Optional[str] = Field(default=None, description="Meal category for this visit")
    entryTime: str = Field(..., description="Timezone-aware ISO 8601 entry timestamp")
    exitTime: str = Field(..., description="Timezone-aware ISO 8601 exit timestamp")
    durationMinutes: int = Field(..., description="Total elapsed dining duration in whole minutes")
    status: str = Field(..., description="Final visit status: 'completed' or 'expired'")
    exitReason: Optional[str] = Field(
        default=None,
        description="Reason visit ended (e.g. 'tray_return', 'timeout')",
    )


class VisitHistoryResponse(BaseModel):
    """Response schema for student dining visit history with pagination."""

    visits: List[VisitHistoryItem] = Field(
        default_factory=list,
        description="List of past dining visits, newest first",
    )
    pagination: PaginationDetails = Field(..., description="Pagination metadata")

