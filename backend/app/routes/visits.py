from typing import Any, Dict
from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_current_student
from app.schemas.visit import CurrentVisitResponse, VisitHistoryResponse
from app.services.visit_service import (
    get_student_current_active_visit,
    get_student_visit_history,
)

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.get(
    "/current",
    response_model=CurrentVisitResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current Active Dining Visit",
    description=(
        "Retrieve the ongoing dining session for the authenticated student, including assigned "
        "seat number, dining hall, entry timestamp, dynamic duration in minutes, and meal type. "
        "If no active session exists, returns active: false with visit: null."
    ),
    responses={
        200: {
            "description": "Visit status retrieved successfully.",
            "content": {
                "application/json": {
                    "examples": {
                        "active": {
                            "summary": "Active Dining Session",
                            "value": {
                                "active": True,
                                "visit": {
                                    "seatNumber": 24,
                                    "diningHall": "Central Mess",
                                    "entryTime": "2026-09-12T22:26:00+05:30",
                                    "durationMinutes": 8,
                                    "mealType": "Dinner",
                                },
                            },
                        },
                        "inactive": {
                            "summary": "No Active Session",
                            "value": {
                                "active": False,
                                "visit": None,
                            },
                        },
                    }
                }
            },
        },
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
    },
)
def get_current_visit(
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> CurrentVisitResponse:
    """Return the authenticated student's active visit details or clean inactive state."""
    student_id = current_student["studentId"]
    return get_student_current_active_visit(student_id)


@router.get(
    "/history",
    response_model=VisitHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student Visit History",
    description=(
        "Retrieve historical completed and expired dining visits for the authenticated student, "
        "sorted newest first by exit timestamp. Active visits are excluded. Supports limit and offset pagination."
    ),
    responses={
        200: {"description": "Visit history retrieved successfully."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
        422: {"description": "Validation error (invalid limit or negative offset)."},
    },
)
def get_visit_history(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of historical visit records to return (1 to 100)",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip for pagination",
    ),
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> VisitHistoryResponse:
    """Retrieve paginated completed and expired visits for the authenticated student."""
    student_id = current_student["studentId"]
    return get_student_visit_history(student_id=student_id, limit=limit, offset=offset)

