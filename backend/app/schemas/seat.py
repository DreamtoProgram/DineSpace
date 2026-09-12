from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class SeatItem(BaseModel):
    """Schema representing an individual virtual seat and its occupancy state."""

    seatNumber: int = Field(..., description="Virtual seat number (1 through capacity)")
    status: Literal["available", "occupied"] = Field(
        ..., description="Current status of the seat: 'available' or 'occupied'"
    )


class SeatMapResponse(BaseModel):
    """Schema representing the dining hall virtual seat map and occupancy counts."""

    diningHall: str = Field(..., description="Dining hall facility name")
    capacity: int = Field(..., description="Configured total virtual seat capacity")
    occupiedCount: int = Field(..., description="Count of currently occupied seats")
    availableCount: int = Field(..., description="Count of currently available open seats")
    mySeat: Optional[int] = Field(
        default=None,
        description="The authenticated student's currently occupied seat number, or null if not dining",
    )
    nextAvailableSeat: Optional[int] = Field(
        default=None,
        description="Lowest-numbered available virtual seat, or null if all seats are occupied",
    )
    seats: List[SeatItem] = Field(
        ..., description="List of virtual seats and their current occupancy statuses"
    )
