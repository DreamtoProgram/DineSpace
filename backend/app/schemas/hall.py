from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.occupancy import StatusResponse


class DiningHallSummary(BaseModel):
    """Schema representing metadata and real-time status of a campus dining hall."""

    id: str = Field(..., description="Unique slug ID for the dining hall")
    name: str = Field(..., description="Human-readable dining hall name")
    campus: str = Field(..., description="Campus sector or zone")
    location: str = Field(..., description="Physical building and floor location")
    capacity: int = Field(..., description="Total virtual seat capacity")
    type: str = Field(..., description="Facility dining type")
    timings: str = Field(..., description="Operational service hours")
    features: List[str] = Field(default_factory=list, description="Facility features and highlights")
    status: Optional[StatusResponse] = Field(default=None, description="Real-time occupancy status")


class DiningHallsListResponse(BaseModel):
    """Schema representing the list of all available dining halls on campus."""

    totalHalls: int = Field(..., description="Number of active dining facilities")
    halls: List[DiningHallSummary] = Field(..., description="List of dining facilities")
    defaultHall: str = Field(default="Central Mess", description="Campus default dining hall")
