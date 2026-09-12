from typing import Any, Dict, Literal, Optional
from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_current_student
from app.schemas.seat import SeatMapResponse
from app.services.seat_service import get_virtual_seat_map

router = APIRouter(prefix="/seats", tags=["Seats"])


@router.get(
    "",
    response_model=SeatMapResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Dining Hall Virtual Seat Map",
    description=(
        "Retrieve the virtual seat map and real-time occupancy counts for a dining hall. "
        "Allows authenticated students to see total capacity, occupied count, available count, "
        "the lowest available seat, their own active seat, and individual seat states (available/occupied). "
        "Supports optional filtering by seat status."
    ),
    responses={
        200: {
            "description": "Virtual seat map and metrics retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "diningHall": "Central Mess",
                        "capacity": 100,
                        "occupiedCount": 37,
                        "availableCount": 63,
                        "mySeat": 24,
                        "nextAvailableSeat": 2,
                        "seats": [
                            {"seatNumber": 1, "status": "available"},
                            {"seatNumber": 2, "status": "occupied"},
                            {"seatNumber": 3, "status": "available"},
                        ],
                    }
                }
            },
        },
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
        422: {"description": "Validation error on query parameters (e.g. invalid status filter)."},
    },
)
def get_seats(
    diningHall: Optional[str] = Query(
        default=None,
        description="Dining hall facility name (defaults to configured Central Mess)",
    ),
    status: Optional[Literal["available", "occupied"]] = Query(
        default=None,
        description="Optional filter on seat status: 'available' or 'occupied'",
    ),
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> SeatMapResponse:
    """Return the virtual seat map for the specified dining hall."""
    student_id = current_student["studentId"]
    return get_virtual_seat_map(
        current_student_id=student_id,
        dining_hall=diningHall,
        status_filter=status,
    )
