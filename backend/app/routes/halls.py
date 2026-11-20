from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.hall import DiningHallSummary, DiningHallsListResponse
from app.services.hall_service import (
    get_all_dining_halls,
    get_hall_by_name_or_id,
)
from app.services.occupancy_service import get_occupancy_status

router = APIRouter(prefix="/halls", tags=["Dining Halls"])


@router.get(
    "",
    response_model=DiningHallsListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Campus Dining Halls",
    description="Retrieve list of all active campus dining halls and multi-campus facilities with live occupancy metrics.",
)
def list_dining_halls(
    includeStatus: bool = Query(
        default=True,
        description="Whether to compute and include real-time occupancy status for each dining facility",
    ),
) -> DiningHallsListResponse:
    """Return all dining facilities across campus."""
    return get_all_dining_halls(include_status=includeStatus)


@router.get(
    "/{hall_id}",
    response_model=DiningHallSummary,
    status_code=status.HTTP_200_OK,
    summary="Get Dining Hall Details",
    description="Retrieve details and live status for a specific dining facility by name or ID.",
    responses={
        200: {"description": "Dining hall details retrieved successfully."},
        404: {"description": "Dining hall not found."},
    },
)
def get_dining_hall(hall_id: str) -> DiningHallSummary:
    """Return details for a single dining hall."""
    hall = get_hall_by_name_or_id(hall_id)
    if not hall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dining hall '{hall_id}' not found.",
        )
    status_info = get_occupancy_status(dining_hall=hall["name"])
    return DiningHallSummary(
        id=hall["id"],
        name=hall["name"],
        campus=hall["campus"],
        location=hall["location"],
        capacity=hall["capacity"],
        type=hall["type"],
        timings=hall["timings"],
        features=hall["features"],
        status=status_info,
    )
