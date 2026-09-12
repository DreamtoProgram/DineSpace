from datetime import datetime
import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.config import get_settings
from app.database import db_manager
from app.services.menu_service import get_campus_timezone
from app.services.occupancy_service import determine_current_meal_type

logger = logging.getLogger(__name__)


def validate_student_pass(student: Dict[str, Any], pass_code: str) -> None:
    """Verify that the scanned passCode matches the authenticated student's pass.

    Args:
        student: Authenticated student document from database.
        pass_code: The passCode provided in the scan request.

    Raises:
        HTTPException(400): If passCode does not match.
    """
    expected_pass = student.get("passCode")
    if not expected_pass or expected_pass != pass_code:
        logger.warning(
            "Pass validation failed for student %s: scanned passCode mismatch.",
            student.get("studentId"),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid dining pass code for this student.",
        )


def check_student_active_visit(student_id: str) -> None:
    """Verify that the student does not already have an active dining visit.

    Args:
        student_id: Student unique identification.

    Raises:
        HTTPException(409): If an active visit already exists for this student.
    """
    try:
        active_visit = db_manager.occupancy.find_one(
            {"studentId": student_id, "status": "occupied"}
        )
        if active_visit:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have an active dining visit.",
            )
    except HTTPException:
        raise
    except PyMongoError as exc:
        logger.error("Database query error checking active visit for %s: %s", student_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error checking active visits.",
        )


def assign_virtual_seat_and_checkin(
    student: Dict[str, Any],
    pass_code: str,
    dining_hall: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate student pass, check active visit, and assign the lowest available virtual seat.

    Ensures concurrency protection via MongoDB partial unique index on (diningHall, seatNumber).

    Args:
        student: Authenticated student document.
        pass_code: Scanned pass code string.
        dining_hall: Target dining hall name (defaults to configured DEFAULT_DINING_HALL).

    Returns:
        The created active occupancy document.

    Raises:
        HTTPException(400): If pass code is invalid.
        HTTPException(409): If student is already active or mess is at full capacity.
    """
    settings = get_settings()
    student_id = student["studentId"]
    hall = dining_hall or settings.DEFAULT_DINING_HALL
    total_seats = settings.TOTAL_SEATS

    # 1. Validate scanned pass code
    validate_student_pass(student, pass_code)

    # 2. Prevent duplicate active visits for the same student
    check_student_active_visit(student_id)

    # 3. Query all currently occupied seat numbers in the target dining hall
    try:
        occupied_seats = set(
            db_manager.occupancy.distinct(
                "seatNumber",
                {"diningHall": hall, "status": "occupied"},
            )
        )
    except PyMongoError as exc:
        logger.error("Failed to query occupied seats: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error retrieving seat occupancy.",
        )

    # Check if mess is already full
    if len(occupied_seats) >= total_seats:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No seats are currently available.",
        )

    # Identify candidate available seats in ascending order (lowest seat number first)
    available_candidates = [
        seat_num for seat_num in range(1, total_seats + 1)
        if seat_num not in occupied_seats
    ]

    if not available_candidates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No seats are currently available.",
        )

    # 4. Attempt atomic reservation for the lowest free seat with race-condition retry
    for candidate_seat in available_candidates:
        entry_time_iso = datetime.now(get_campus_timezone()).isoformat()
        current_meal = determine_current_meal_type()

        occupancy_record = {
            "studentId": student_id,
            "seatNumber": candidate_seat,
            "diningHall": hall,
            "entryTime": entry_time_iso,
            "exitTime": None,
            "status": "occupied",
            "mealType": current_meal,
        }

        try:
            db_manager.occupancy.insert_one(occupancy_record)
            logger.info(
                "Assigned virtual seat #%d at %s to student %s (%s)",
                candidate_seat,
                hall,
                student_id,
                student.get("name"),
            )
            return occupancy_record
        except DuplicateKeyError as exc:
            err_str = str(exc)
            # If the duplicate key was on studentId, student already entered in another concurrent request
            if "studentId" in err_str:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="You already have an active dining visit.",
                )
            # If the duplicate key was on (diningHall, seatNumber), another student claimed this seat concurrently
            logger.warning(
                "Seat #%d at %s was concurrently claimed by another student. Trying next free seat...",
                candidate_seat,
                hall,
            )
            continue
        except PyMongoError as exc:
            logger.error("Failed to insert occupancy record: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error reserving seat.",
            )

    # If all candidate seats were concurrently claimed
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="No seats are currently available.",
    )
