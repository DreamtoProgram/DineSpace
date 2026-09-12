from typing import List
from pydantic import BaseModel, Field


class MenuItemModel(BaseModel):
    """Internal domain model for a dish item on the menu."""

    name: str = Field(..., description="Name of the dish or food item")
    description: str = Field(default="", description="Short description of the dish")


class MenuDocument(BaseModel):
    """Internal domain model representing a menu document in MongoDB."""

    date: str = Field(..., description="Date of the menu in YYYY-MM-DD format")
    mealType: str = Field(..., description="Meal type (e.g. Lunch, Dinner)")
    items: List[MenuItemModel] = Field(default_factory=list, description="List of dishes for the meal")
