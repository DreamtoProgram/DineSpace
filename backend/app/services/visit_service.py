from datetime import datetime
import logging
from typing import Any, Optional

from fastapi import HTTPException, status
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from app.database import db_manager
from app.schemas.scan import CompletedVisitDetails
from app.schemas.visit import (
    ActiveVisitDetails,
    CurrentVisitResponse,
    PaginationDetails,
    VisitHistoryItem,
    VisitHistoryResponse,
)
from app.services.menu_service import get_campus_timezone

logger = logging.getLogger(__name__)


def calculate_visit_duration_minutes(
    entry_time_val: Any,
    now_dt: Optional[datetime] = None,
) -> int:
    """Calculate the elapsed duration of a visit in whole minutes.

    Args:
        entry_time_val: Either an ISO-8601 string or a datetime object.
        now_dt: Optional reference timestamp (defaults to now in campus timezone).

    Returns:
        Non-negative integer representing elapsed whole minutes.
    """
    if now_dt is None:
        now_dt = datetime.now(get_campus_timezone())
    elif isinstance(now_dt, str):
        try:
            now_dt = datetime.fromisoformat(now_dt)
        except ValueError:
            logger.error("Failed to parse reference exit timestamp string: %s", now_dt)
            now_dt = datetime.now(get_campus_timezone())

    if now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=get_campus_timezone())

    if isinstance(entry_time_val, str):
        try:
            entry_dt = datetime.fromisoformat(entry_time_val)
        except ValueError:
            logger.error("Failed to parse entryTime string: %s", entry_time_val)
            return 0
    elif isinstance(entry_time_val, datetime):
        entry_dt = entry_time_val
    else:
        return 0

    if entry_dt.tzinfo is None:
        entry_dt = entry_dt.replace(tzinfo=get_campus_timezone())

    delta_seconds = (now_dt - entry_dt).total_seconds()
    return max(0, int(delta_seconds // 60))



def get_student_current_active_visit(
    student_id: str,
    now_dt: Optional[datetime] = None,
) -> CurrentVisitResponse:
    """Retrieve the currently active dining visit for an authenticated student.

    Args:
        student_id: Unique student identifier.
        now_dt: Optional reference timestamp for testing duration calculations.

    Returns:
        CurrentVisitResponse with active=True and details, or active=False and visit=None.
    """
    try:
        cursor = db_manager.occupancy.find(
            {
                "studentId": student_id,
                "status": "occupied",
                "exitTime": None,
            }
        ).sort("entryTime", -1)
        records = list(cursor)
    except PyMongoError as exc:
        logger.error("Database error fetching active visit for %s: %s", student_id, exc)
        # Return clean inactive state instead of crashing when DB encounters an issue
        return CurrentVisitResponse(active=False, visit=None)

    if not records:
        return CurrentVisitResponse(active=False, visit=None)

    if len(records) > 1:
        logger.warning(
            "Data inconsistency detected: Student %s has %d active occupancy records. Returning most recent.",
            student_id,
            len(records),
        )

    record = records[0]
    raw_entry = record.get("entryTime")
    duration = calculate_visit_duration_minutes(raw_entry, now_dt)
    entry_iso = raw_entry.isoformat() if isinstance(raw_entry, datetime) else str(raw_entry)

    return CurrentVisitResponse(
        active=True,
        visit=ActiveVisitDetails(
            seatNumber=record["seatNumber"],
            diningHall=record.get("diningHall", "Central Mess"),
            entryTime=entry_iso,
            durationMinutes=duration,
            mealType=record.get("mealType"),
        ),
    )


def complete_current_visit(
    student_id: str,
    exit_time_dt: Optional[datetime] = None,
) -> CompletedVisitDetails:
    """Complete an authenticated student's active dining visit, release their seat, and record exit.

    Performs an atomic update using MongoDB's find_one_and_update to ensure race condition safety
    and prevent duplicate/repeated exit operations from corrupting the visit record.

    Args:
        student_id: Unique student identifier.
        exit_time_dt: Optional exit timestamp (defaults to current time in campus timezone).

    Returns:
        CompletedVisitDetails with seatNumber, diningHall, entryTime, exitTime, duration, mealType.

    Raises:
        HTTPException(409): If no active dining visit exists for the student.
        HTTPException(500): If database error or internal timestamp inconsistency occurs.
    """
    campus_tz = get_campus_timezone()
    if exit_time_dt is None:
        exit_time_dt = datetime.now(campus_tz)
    elif exit_time_dt.tzinfo is None:
        exit_time_dt = exit_time_dt.replace(tzinfo=campus_tz)
    exit_time_iso = exit_time_dt.isoformat()

    # 1. Look for active occupancy record
    try:
        active_record = db_manager.occupancy.find_one(
            {
                "studentId": student_id,
                "status": "occupied",
                "exitTime": None,
            },
            sort=[("entryTime", -1)],
        )
    except PyMongoError as exc:
        logger.error("Database query failed while finding active visit for %s: %s", student_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error finding active visit.",
        )

    if not active_record:
        logger.info("Exit scan rejected: No active visit found for student %s", student_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No active dining visit found.",
        )

    # 2. Timestamp and record integrity validation
    raw_entry = active_record.get("entryTime")
    if not raw_entry:
        logger.error("Occupancy record %s for student %s has missing entryTime", active_record.get("_id"), student_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error: active visit record contains invalid timestamp.",
        )

    if isinstance(raw_entry, str):
        try:
            entry_dt = datetime.fromisoformat(raw_entry)
        except ValueError:
            logger.error("Occupancy record %s has unparseable entryTime: %s", active_record.get("_id"), raw_entry)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error: active visit record contains invalid timestamp.",
            )
    elif isinstance(raw_entry, datetime):
        entry_dt = raw_entry
    else:
        logger.error("Occupancy record %s has non-datetime entryTime: %s", active_record.get("_id"), type(raw_entry))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error: active visit record contains invalid timestamp.",
        )

    if entry_dt.tzinfo is None:
        entry_dt = entry_dt.replace(tzinfo=campus_tz)

    if entry_dt > exit_time_dt:
        logger.error(
            "Time anomaly: entryTime (%s) is later than exitTime (%s) for record %s",
            entry_dt,
            exit_time_dt,
            active_record.get("_id"),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error: exit timestamp cannot precede entry timestamp.",
        )

    # 3. Atomic MongoDB update ensuring exactly one concurrent worker completes the visit
    try:
        updated_record = db_manager.occupancy.find_one_and_update(
            filter={
                "_id": active_record["_id"],
                "status": "occupied",
                "exitTime": None,
            },
            update={
                "$set": {
                    "status": "completed",
                    "exitTime": exit_time_iso,
                    "exitReason": "tray_return",
                }
            },
            return_document=ReturnDocument.AFTER,
        )
    except PyMongoError as exc:
        logger.error("Database update failed while completing visit for %s: %s", student_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error completing visit.",
        )

    if not updated_record:
        logger.warning("Visit for %s was completed concurrently by another request", student_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No active dining visit found.",
        )

    # 4. Calculate total duration in whole minutes
    duration_minutes = calculate_visit_duration_minutes(raw_entry, exit_time_dt)
    entry_iso = entry_dt.isoformat()

    logger.info(
        "Completed visit for student %s: Seat #%d at %s released (duration: %d mins)",
        student_id,
        updated_record["seatNumber"],
        updated_record.get("diningHall", "Central Mess"),
        duration_minutes,
    )

    # 5. Create notification for successful visit completion
    try:
        from app.services.notification_service import create_notification

        create_notification(
            student_id=student_id,
            notification_type="visit",
            title="Visit completed",
            message="Your dining visit has been completed.",
            metadata={
                "seatNumber": updated_record["seatNumber"],
                "durationMinutes": duration_minutes,
                "exitReason": "tray_return",
            },
        )
    except Exception as exc:
        logger.error("Failed to create visit completion notification for %s: %s", student_id, exc)

    return CompletedVisitDetails(
        seatNumber=updated_record["seatNumber"],
        diningHall=updated_record.get("diningHall", "Central Mess"),
        entryTime=entry_iso,
        exitTime=exit_time_iso,
        durationMinutes=duration_minutes,
        mealType=updated_record.get("mealType"),
    )


def get_student_visit_history(
    student_id: str,
    limit: int = 20,
    offset: int = 0,
) -> VisitHistoryResponse:
    """Retrieve historical completed and expired dining visits for the authenticated student.

    Sorted newest first by exitTime descending, with skip/limit pagination.
    Active visits (status == 'occupied') are excluded.

    Args:
        student_id: Unique student identifier.
        limit: Maximum number of records to return.
        offset: Number of records to skip.

    Returns:
        VisitHistoryResponse containing visits list and pagination metadata.
    """
    filter_query = {
        "studentId": student_id,
        "status": {"$in": ["completed", "expired"]},
    }

    try:
        total_count = db_manager.occupancy.count_documents(filter_query)
        cursor = (
            db_manager.occupancy.find(filter_query)
            .sort("exitTime", -1)
            .skip(offset)
            .limit(limit)
        )
        records = list(cursor)
    except PyMongoError as exc:
        logger.error("Database error retrieving visit history for %s: %s", student_id, exc)
        return VisitHistoryResponse(
            visits=[],
            pagination=PaginationDetails(limit=limit, offset=offset, total=0),
        )

    visits_list = []
    for doc in records:
        raw_entry = doc.get("entryTime")
        raw_exit = doc.get("exitTime")

        # Compute duration on-the-fly from entryTime and exitTime
        duration = calculate_visit_duration_minutes(raw_entry, raw_exit)

        entry_iso = raw_entry.isoformat() if isinstance(raw_entry, datetime) else str(raw_entry)
        exit_iso = raw_exit.isoformat() if isinstance(raw_exit, datetime) else str(raw_exit)

        exit_reason = doc.get("exitReason")
        if not exit_reason:
            if doc.get("status") == "completed":
                exit_reason = "tray_return"
            elif doc.get("status") == "expired":
                exit_reason = "timeout"

        visits_list.append(
            VisitHistoryItem(
                seatNumber=doc["seatNumber"],
                diningHall=doc.get("diningHall", "Central Mess"),
                mealType=doc.get("mealType"),
                entryTime=entry_iso,
                exitTime=exit_iso,
                durationMinutes=duration,
                status=doc["status"],
                exitReason=exit_reason,
            )
        )

    return VisitHistoryResponse(
        visits=visits_list,
        pagination=PaginationDetails(
            limit=limit,
            offset=offset,
            total=total_count,
        ),
    )


