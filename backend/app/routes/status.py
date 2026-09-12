from fastapi import APIRouter, status

from app.schemas.occupancy import StatusResponse
from app.services.occupancy_service import get_occupancy_status

router = APIRouter(tags=["Status"])


@router.get(
    "/status",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Dining Hall Occupancy Status",
    description=(
        "Retrieve real-time dining hall crowd percentage, seat counts (total, occupied, available), "
        "crowd level (Low, Moderate, Peak Rush), and current meal period. Designed for 3-second polling "
        "from the Home dashboard."
    ),
    responses={
        200: {
            "description": "Live occupancy and crowd status successfully computed.",
            "content": {
                "application/json": {
                    "example": {
                        "totalSeats": 100,
                        "occupiedSeats": 58,
                        "availableSeats": 42,
                        "occupancyPercentage": 58,
                        "crowdLevel": "Moderate",
                        "mealType": "Lunch",
                        "updatedAt": "2026-09-12T13:30:00+05:30",
                    }
                }
            },
        }
    },
)
def get_status() -> StatusResponse:
    """Return live occupancy metrics for the dining hall."""
    return get_occupancy_status()
