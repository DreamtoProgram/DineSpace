from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_student
from app.schemas.auth import StudentPublic
from app.schemas.scan import (
    EntryScanRequest,
    EntrySuccessResponse,
    ExitScanRequest,
    ExitSuccessResponse,
)
from app.services.entry_service import assign_virtual_seat_and_checkin
from app.services.visit_service import complete_current_visit

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.post(
    "/entry",
    response_model=EntrySuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Dining Hall Entry Scan",
    description=(
        "Scan an authenticated student's entry pass code to check in and reserve the next "
        "lowest available virtual seat. Requires Bearer JWT token."
    ),
    responses={
        200: {"description": "Entry successful; virtual seat assigned."},
        400: {"description": "Scanned passCode does not match authenticated student."},
        401: {"description": "Authentication missing, invalid, or expired."},
        403: {"description": "Student account is inactive."},
        409: {"description": "Student already has an active dining visit or dining hall is full."},
        422: {"description": "Validation error (e.g. missing passCode)."},
    },
)
def scan_entry(
    payload: EntryScanRequest,
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> EntrySuccessResponse:
    """Validate entry pass, assign lowest available virtual seat, and create occupancy record."""
    record = assign_virtual_seat_and_checkin(
        student=current_student,
        pass_code=payload.passCode,
        dining_hall=payload.diningHall,
    )

    return EntrySuccessResponse(
        success=True,
        message="Entry successful",
        student=StudentPublic(
            studentId=current_student["studentId"],
            name=current_student["name"],
        ),
        seatNumber=record["seatNumber"],
        diningHall=record["diningHall"],
        entryTime=record["entryTime"],
        mealType=record.get("mealType"),
    )


@router.post(
    "/exit",
    response_model=ExitSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Dining Hall Tray Return / Exit Scan",
    description=(
        "Complete the authenticated student's active dining visit upon tray return. "
        "Atomically records exit timestamp, calculates elapsed duration, releases the virtual seat, "
        "and updates the crowd status. Requires Bearer JWT token."
    ),
    responses={
        200: {"description": "Visit completed successfully; virtual seat released."},
        400: {"description": "Invalid scanType provided."},
        401: {"description": "Authentication missing, invalid, or expired."},
        403: {"description": "Student account is inactive."},
        409: {"description": "No active dining visit found for this student."},
        422: {"description": "Request validation error."},
        500: {"description": "Internal database or timestamp validation error."},
    },
)
def scan_exit(
    payload: Optional[ExitScanRequest] = None,
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> ExitSuccessResponse:
    """Validate tray return scan, atomically complete active visit, and release virtual seat."""
    if payload and payload.scanType and payload.scanType != "tray_return":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scanType. Expected 'tray_return'.",
        )

    completed_visit = complete_current_visit(student_id=current_student["studentId"])

    return ExitSuccessResponse(
        success=True,
        message="Visit completed successfully",
        visit=completed_visit,
    )

