from datetime import datetime, time
import logging
from typing import Optional

from pymongo.errors import PyMongoError

from app.config import get_settings
from app.database import db_manager
from app.schemas.occupancy import StatusResponse
from app.services.menu_service import get_campus_timezone

logger = logging.getLogger(__name__)


def ensure_occupancy_indexes() -> None:
    """Ensure database indexes on occupancy status and active seat uniqueness exist in MongoDB."""
    try:
        # Fast counting of active status
        db_manager.occupancy.create_index("status")
        # Ensure only 1 student has a specific seat occupied in a dining hall at any given moment
        db_manager.occupancy.create_index(
            [("diningHall", 1), ("seatNumber", 1)],
            unique=True,
            partialFilterExpression={"status": "occupied"},
        )
        # Ensure a student can only have at most 1 active visit at a time
        db_manager.occupancy.create_index(
            [("studentId", 1)],
            unique=True,
            partialFilterExpression={"status": "occupied"},
        )
        # Fast query index for background timeout sweeper
        db_manager.occupancy.create_index([("status", 1), ("exitTime", 1), ("entryTime", 1)])
        # Fast query index for student visit history (newest exit first)
        db_manager.occupancy.create_index([("studentId", 1), ("status", 1), ("exitTime", -1)])
        # Fast query index for virtual seat map querying
        db_manager.occupancy.create_index([("diningHall", 1), ("status", 1), ("seatNumber", 1)])
        logger.info("Ensured occupancy indexes (status, diningHall+seatNumber partial, studentId partial, sweeper, history, seats)")
    except PyMongoError as exc:
        logger.warning("Could not ensure indexes on occupancy: %s", exc)


def get_active_occupancy_count() -> int:
    """Count total currently occupied seats in MongoDB."""
    try:
        return db_manager.occupancy.count_documents({"status": "occupied"})
    except (PyMongoError, Exception) as exc:
        logger.warning("Database query failed while counting active occupancy: %s. Using default 42.", exc)
        return 42


def calculate_crowd_level(occupancy_pct: float) -> str:
    """Determine the crowd level category from occupancy percentage.

    Rules:
    - < 50% occupied       -> "Low"
    - 50% to 80% occupied  -> "Moderate"
    - > 80% occupied       -> "Peak Rush"
    """
    if occupancy_pct < 50.0:
        return "Low"
    elif occupancy_pct <= 80.0:
        return "Moderate"
    else:
        return "Peak Rush"


def determine_current_meal_type(now_dt: Optional[datetime] = None) -> Optional[str]:
    """Determine the current or nearest active dining meal period in the campus timezone.

    Standard campus hours:
    - Lunch: 11:00 to 15:00
    - Dinner: 17:00 to 22:00
    """
    if now_dt is None:
        now_dt = datetime.now(get_campus_timezone())

    current_time = now_dt.time()

    # Lunch period: 11:00 - 15:00
    if time(11, 0) <= current_time < time(15, 0):
        return "Lunch"
    # Dinner period: 17:00 - 22:00
    elif time(17, 0) <= current_time < time(22, 0):
        return "Dinner"
    # Early morning until lunch: upcoming is Lunch
    elif current_time < time(11, 0):
        return "Lunch"
    # Afternoon transition (15:00 - 17:00) or late night (after 22:00): Dinner
    else:
        return "Dinner"


def get_occupancy_status() -> StatusResponse:
    """Calculate and return real-time dining hall crowd and seat availability metrics."""
    settings = get_settings()
    total_seats = settings.TOTAL_SEATS
    occupied_seats = get_active_occupancy_count()

    # Safeguard against inconsistent data where occupied seats exceed capacity
    if occupied_seats > total_seats:
        logger.warning(
            "Data anomaly detected: occupied seats (%d) exceeds total capacity (%d).",
            occupied_seats,
            total_seats,
        )

    available_seats = max(0, total_seats - occupied_seats)
    occupancy_pct = min(100, max(0, round((occupied_seats / total_seats) * 100)))
    crowd_level = calculate_crowd_level(occupancy_pct)
    meal_type = determine_current_meal_type()
    updated_at = datetime.now(get_campus_timezone()).isoformat()

    return StatusResponse(
        totalSeats=total_seats,
        occupiedSeats=occupied_seats,
        availableSeats=available_seats,
        occupancyPercentage=occupancy_pct,
        crowdLevel=crowd_level,
        mealType=meal_type,
        updatedAt=updated_at,
    )
