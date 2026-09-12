from typing import Optional
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Schema representing real-time dining hall crowd and seat occupancy status."""

    totalSeats: int = Field(..., description="Total dining hall virtual seat capacity")
    occupiedSeats: int = Field(..., description="Currently occupied seats count")
    availableSeats: int = Field(..., description="Currently available open seats count")
    occupancyPercentage: int = Field(..., description="Percentage of occupied seats (0 to 100)")
    crowdLevel: str = Field(..., description="Crowd level categorization: 'Low', 'Moderate', or 'Peak Rush'")
    mealType: Optional[str] = Field(default=None, description="Current or upcoming meal period (e.g. Lunch, Dinner)")
    updatedAt: str = Field(..., description="Timezone-aware ISO 8601 timestamp when status was computed")
