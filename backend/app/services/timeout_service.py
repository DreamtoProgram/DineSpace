from datetime import datetime, timedelta
import logging
from typing import Optional

from pymongo.errors import PyMongoError

from app.config import get_settings
from app.database import db_manager
from app.services.menu_service import get_campus_timezone

logger = logging.getLogger(__name__)


def expire_abandoned_visits(
    now_dt: Optional[datetime] = None,
    timeout_minutes: Optional[int] = None,
) -> int:
    """Find and atomically expire active dining visits that have been occupied for MORE THAN 25 minutes.

    Matching criteria:
    - status == "occupied"
    - exitTime == None
    - entryTime < (now - timeout_minutes) [strict < comparison]

    Updates matching records to:
    - status = "expired"
    - exitTime = current timestamp
    - exitReason = "timeout"

    Preserves records in the occupancy collection for future visit history.
    Because status changes from "occupied" to "expired", virtual seats are immediately freed
    and GET /api/status automatically reflects the freed seats.

    Args:
        now_dt: Reference current timestamp (defaults to now in campus timezone).
        timeout_minutes: Cutoff threshold in minutes (defaults to SEAT_TIMEOUT_MINUTES from settings).

    Returns:
        Number of occupancy documents that were expired.
    """
    settings = get_settings()
    campus_tz = get_campus_timezone()

    if now_dt is None:
        now_dt = datetime.now(campus_tz)
    elif now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=campus_tz)

    if timeout_minutes is None:
        timeout_minutes = settings.SEAT_TIMEOUT_MINUTES

    cutoff_dt = now_dt - timedelta(minutes=timeout_minutes)
    cutoff_iso = cutoff_dt.isoformat()
    now_iso = now_dt.isoformat()

    # Query matches only active sessions strictly older than the cutoff
    filter_query = {
        "status": "occupied",
        "exitTime": None,
        "$or": [
            {"entryTime": {"$lt": cutoff_iso}},
            {"entryTime": {"$lt": cutoff_dt}},
        ],
    }

    update_query = {
        "$set": {
            "status": "expired",
            "exitTime": now_iso,
            "exitReason": "timeout",
        }
    }

    try:
        from pymongo import ReturnDocument
        from app.services.notification_service import create_notification
        from app.services.visit_service import calculate_visit_duration_minutes

        candidates = list(db_manager.occupancy.find(filter_query))
        expired_count = 0

        for candidate in candidates:
            # Atomically expire each candidate document to guarantee race safety
            expired_doc = db_manager.occupancy.find_one_and_update(
                filter={
                    "_id": candidate["_id"],
                    "status": "occupied",
                    "exitTime": None,
                },
                update={
                    "$set": {
                        "status": "expired",
                        "exitTime": now_iso,
                        "exitReason": "timeout",
                    }
                },
                return_document=ReturnDocument.AFTER,
            )
            if expired_doc:
                expired_count += 1
                try:
                    duration = calculate_visit_duration_minutes(expired_doc.get("entryTime"), now_dt)
                    create_notification(
                        student_id=expired_doc["studentId"],
                        notification_type="visit",
                        title="Visit timed out",
                        message="Your dining visit was automatically closed after the seat timeout.",
                        metadata={
                            "seatNumber": expired_doc["seatNumber"],
                            "durationMinutes": duration,
                            "exitReason": "timeout",
                        },
                    )
                except Exception as notif_exc:
                    logger.error(
                        "Failed to create timeout notification for student %s: %s",
                        expired_doc.get("studentId"),
                        notif_exc,
                    )

        if expired_count > 0:
            logger.info(
                "Expired %d abandoned dining visit(s) (occupied for > %d minutes)",
                expired_count,
                timeout_minutes,
            )
        return expired_count
    except PyMongoError as exc:
        logger.error("Database error during abandoned visit expiration: %s", exc)
        return 0

