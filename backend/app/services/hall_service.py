import logging
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.schemas.hall import DiningHallSummary, DiningHallsListResponse
from app.services.occupancy_service import get_occupancy_status

logger = logging.getLogger(__name__)

CAMPUS_DINING_HALLS: List[Dict[str, Any]] = [
    {
        "id": "central-mess",
        "name": "Central Mess",
        "campus": "Main Campus",
        "location": "Sector A, Central Dining Complex",
        "capacity": 100,
        "type": "Standard Student Mess",
        "timings": "7:00 AM - 10:00 PM",
        "features": ["Vegetarian & Non-Veg", "Wheelchair Accessible", "High Throughput", "Express Tray Return"],
    },
    {
        "id": "north-hostel-mess",
        "name": "North Hostel Mess",
        "campus": "North Campus",
        "location": "Hostel Cluster 4, Ground Floor",
        "capacity": 80,
        "type": "Hostel Dining Facility",
        "timings": "7:30 AM - 9:30 PM",
        "features": ["Hostel Dining", "Study Lounge Attached", "Quick Breakfast Counter"],
    },
    {
        "id": "food-court",
        "name": "Food Court (Student Center)",
        "campus": "South Campus",
        "location": "Student Activity Center, Level 1",
        "capacity": 120,
        "type": "Multi-Cuisine Hub",
        "timings": "8:00 AM - 11:00 PM",
        "features": ["Multi-Cuisine", "Extended Hours", "Beverage Bar", "Open Terrace Seating"],
    },
]


def get_all_dining_halls(include_status: bool = True) -> DiningHallsListResponse:
    """Return all campus dining halls, optionally computing live occupancy metrics for each."""
    settings = get_settings()
    results: List[DiningHallSummary] = []

    for hall in CAMPUS_DINING_HALLS:
        status_payload = None
        if include_status:
            try:
                status_payload = get_occupancy_status(dining_hall=hall["name"])
            except Exception as exc:
                logger.warning("Could not compute status for hall %s: %s", hall["name"], exc)

        results.append(
            DiningHallSummary(
                id=hall["id"],
                name=hall["name"],
                campus=hall["campus"],
                location=hall["location"],
                capacity=hall["capacity"],
                type=hall["type"],
                timings=hall["timings"],
                features=hall["features"],
                status=status_payload,
            )
        )

    return DiningHallsListResponse(
        totalHalls=len(results),
        halls=results,
        defaultHall=settings.DEFAULT_DINING_HALL,
    )


def get_hall_by_name_or_id(identifier: str) -> Optional[Dict[str, Any]]:
    """Resolve a dining hall specification by either its human name or slug ID."""
    clean = identifier.strip().lower()
    for hall in CAMPUS_DINING_HALLS:
        if hall["id"].lower() == clean or hall["name"].lower() == clean:
            return hall
    return None


def get_hall_capacity(dining_hall: Optional[str]) -> int:
    """Return total virtual seats for a dining hall, defaulting to configuration."""
    settings = get_settings()
    if not dining_hall:
        return settings.TOTAL_SEATS
    hall = get_hall_by_name_or_id(dining_hall)
    if hall:
        return hall["capacity"]
    return settings.TOTAL_SEATS
