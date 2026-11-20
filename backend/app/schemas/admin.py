from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from app.schemas.menu import MenuItem


class SeatStatusUpdateRequest(BaseModel):
    """Schema for updating a seat's operational status."""

    seatNumber: int = Field(..., ge=1, le=100, description="Virtual seat number (1..100)")
    status: Literal["available", "maintenance", "reserved"] = Field(
        ..., description="New seat state: available, maintenance, or reserved"
    )
    note: Optional[str] = Field(default=None, description="Reason or note for maintenance/reservation")
    diningHall: Optional[str] = Field(default="Central Mess", description="Target dining hall")


class SeatReleaseRequest(BaseModel):
    """Schema for force-releasing a stuck seat."""

    seatNumber: int = Field(..., ge=1, le=100, description="Virtual seat number to release")
    reason: Optional[str] = Field(default="Manager override", description="Release reason")
    diningHall: Optional[str] = Field(default="Central Mess", description="Target dining hall")


class MenuItemCreateRequest(BaseModel):
    """Schema for adding a new item to a meal's menu."""

    mealType: str = Field(..., description="Meal category: Lunch, Dinner, Breakfast, Snacks")
    item: MenuItem = Field(..., description="Menu item details")
    date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format (defaults to today)")


class MenuItemUpdateRequest(BaseModel):
    """Schema for updating an existing menu item."""

    mealType: str = Field(..., description="Meal category")
    itemName: str = Field(..., description="Name of the existing item to update")
    item: MenuItem = Field(..., description="New menu item details")
    date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format")


class MenuItemDeleteRequest(BaseModel):
    """Schema for deleting a menu item."""

    mealType: str = Field(..., description="Meal category")
    itemName: str = Field(..., description="Name of the item to delete")
    date: Optional[str] = Field(default=None, description="Date in YYYY-MM-DD format")
