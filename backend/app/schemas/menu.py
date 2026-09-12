from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class MealType(str, Enum):
    """Supported dining meal types."""

    LUNCH = "Lunch"
    DINNER = "Dinner"


class MenuItem(BaseModel):
    """Individual food dish on a menu."""

    name: str = Field(..., min_length=1, description="Name of the food item")
    description: str = Field(default="", description="Description of the food item")


class MealMenu(BaseModel):
    """Menu items for a specific meal type."""

    mealType: MealType = Field(..., description="Meal type (Lunch or Dinner)")
    items: List[MenuItem] = Field(..., description="List of food items served")


class SingleMenuResponse(BaseModel):
    """Response schema for a single meal menu on a given date."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    mealType: MealType = Field(..., description="Meal type (Lunch or Dinner)")
    items: List[MenuItem] = Field(..., description="List of food items served")


class DayMenusResponse(BaseModel):
    """Response schema for all meal menus on a specific date (e.g. today's menu)."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    menus: List[MealMenu] = Field(..., description="List of meal menus available for the day")
