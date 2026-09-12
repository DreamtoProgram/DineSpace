from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OccupancyRecord(BaseModel):
    """Internal domain model representing a seat occupancy document in MongoDB."""

    seatNumber: int = Field(..., description="Virtual seat slot number")
    entryTime: datetime = Field(..., description="Timestamp of dining hall entry")
    exitTime: Optional[datetime] = Field(default=None, description="Timestamp of exit or timeout")
    status: str = Field(default="occupied", description="Seat status: 'occupied', 'completed', 'expired'")
    mealType: Optional[str] = Field(default=None, description="Meal category for this visit")
    studentId: Optional[str] = Field(default=None, description="Associated student ID")
    diningHall: str = Field(default="Central Mess", description="Dining hall facility name")
