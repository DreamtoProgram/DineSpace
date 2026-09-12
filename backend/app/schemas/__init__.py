"""Pydantic schemas for request validation and response serialization."""

from app.schemas.auth import LoginRequest, LoginResponse, StudentPublic
from app.schemas.health import HealthResponse
from app.schemas.menu import (
    DayMenusResponse,
    MealMenu,
    MealType,
    MenuItem,
    SingleMenuResponse,
)
from app.schemas.occupancy import StatusResponse
from app.schemas.scan import EntryScanRequest, EntrySuccessResponse
from app.schemas.seat import SeatItem, SeatMapResponse
from app.schemas.settings import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    SettingsResponse,
    StudentPreferences,
    UpdateSettingsRequest,
)
from app.schemas.visit import ActiveVisitDetails, CurrentVisitResponse

__all__ = [
    "ActiveVisitDetails",
    "ChangePasswordRequest",
    "ChangePasswordResponse",
    "CurrentVisitResponse",
    "DayMenusResponse",
    "EntryScanRequest",
    "EntrySuccessResponse",
    "HealthResponse",
    "LoginRequest",
    "LoginResponse",
    "MealMenu",
    "MealType",
    "MenuItem",
    "SeatItem",
    "SeatMapResponse",
    "SettingsResponse",
    "SingleMenuResponse",
    "StatusResponse",
    "StudentPreferences",
    "StudentPublic",
    "UpdateSettingsRequest",
]
