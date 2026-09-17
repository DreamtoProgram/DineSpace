from datetime import datetime
import logging
from typing import Any, Dict, List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from app.database import db_manager
from app.schemas.notification import (
    NotificationItem,
    NotificationListResponse,
)
from app.schemas.visit import PaginationDetails
from app.services.menu_service import get_campus_timezone

logger = logging.getLogger(__name__)

VALID_NOTIFICATION_TYPES = {"menu", "crowd", "visit", "system"}


def ensure_notification_indexes() -> None:
    """Ensure indexes on notifications collection exist for fast user queries and unread counting."""
    if not db_manager.is_connected:
        return
    try:
        db_manager.notifications.create_index([("studentId", 1), ("createdAt", -1)])
        db_manager.notifications.create_index([("studentId", 1), ("read", 1)])
        logger.info("Ensured notifications indexes (studentId+createdAt, studentId+read)")
    except PyMongoError as exc:
        logger.warning("Could not ensure indexes on notifications: %s", exc)


def create_notification(
    student_id: str,
    notification_type: str,
    title: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Create a new notification for an individual student."""
    if not db_manager.is_connected:
        return None
    n_type = notification_type.lower().strip()
    if n_type not in VALID_NOTIFICATION_TYPES:
        logger.warning("Attempted to create notification with invalid type '%s'", notification_type)
        return None

    # Respect student notification preferences
    try:
        student = db_manager.students.find_one(
            {"studentId": student_id},
            projection={"preferences": 1},
        )
        if student and student.get("preferences", {}).get("notificationsEnabled") is False:
            logger.info("Skipping notification for %s: notifications are disabled in preferences", student_id)
            return None
    except PyMongoError as exc:
        logger.warning("Could not check notification preferences for %s: %s", student_id, exc)

    now_iso = datetime.now(get_campus_timezone()).isoformat()
    doc = {
        "studentId": student_id,
        "type": n_type,
        "title": title,
        "message": message,
        "createdAt": now_iso,
        "read": False,
        "metadata": metadata or {},
    }
    try:
        res = db_manager.notifications.insert_one(doc)
        doc["id"] = str(res.inserted_id)
        logger.info("Created %s notification for student %s: '%s'", n_type, student_id, title)
        return doc
    except PyMongoError as exc:
        logger.error("Failed to insert notification for %s: %s", student_id, exc)
        return None


def get_student_notifications(
    student_id: str,
    notification_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> NotificationListResponse:
    """Retrieve notifications belonging to the authenticated student with pagination."""
    if not db_manager.is_connected:
        now_str = datetime.now(get_campus_timezone()).isoformat()
        sample_notifs = [
            NotificationItem(
                id="notif-1",
                type="menu",
                title="Dinner Menu Updated",
                message="Today's dinner features Shahi Paneer, Mixed Dal Tadka, and fresh Rasgulla.",
                createdAt=now_str,
                read=False,
                metadata={"category": "menu"},
            ),
            NotificationItem(
                id="notif-2",
                type="crowd",
                title="Optimal Dining Window",
                message="Current mess occupancy is at 42% (Low Crowd). Great time to visit Central Mess.",
                createdAt=now_str,
                read=True,
                metadata={"category": "crowd"},
            ),
            NotificationItem(
                id="notif-3",
                type="system",
                title="Digital Tray Scan Active",
                message="Remember to scan tray return kiosk after your meal to earn clean dining karma points.",
                createdAt=now_str,
                read=True,
                metadata={"category": "system"},
            ),
        ]
        if notification_type and notification_type.lower() != "all":
            sample_notifs = [n for n in sample_notifs if n.type == notification_type.lower()]
        return NotificationListResponse(
            notifications=sample_notifs,
            unreadCount=1,
            pagination=PaginationDetails(limit=limit, offset=offset, total=len(sample_notifs)),
        )

    query_filter: Dict[str, Any] = {"studentId": student_id}

    if notification_type:
        n_type = notification_type.lower().strip()
        if n_type != "all":
            if n_type not in VALID_NOTIFICATION_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid notification type '{notification_type}'. Allowed types: menu, crowd, visit, system, all.",
                )
            query_filter["type"] = n_type

    try:
        # Total unread count for the authenticated student across all categories
        unread_count = db_manager.notifications.count_documents(
            {"studentId": student_id, "read": False}
        )
        total_matching = db_manager.notifications.count_documents(query_filter)

        cursor = (
            db_manager.notifications.find(query_filter)
            .sort("createdAt", -1)
            .skip(offset)
            .limit(limit)
        )
        docs = list(cursor)
    except PyMongoError as exc:
        logger.error("Database error fetching notifications for %s: %s", student_id, exc)
        return NotificationListResponse(
            notifications=[],
            unreadCount=0,
            pagination=PaginationDetails(limit=limit, offset=offset, total=0),
        )

    items: List[NotificationItem] = []
    for d in docs:
        raw_created = d.get("createdAt")
        created_iso = (
            raw_created.isoformat() if isinstance(raw_created, datetime) else str(raw_created)
        )
        items.append(
            NotificationItem(
                id=str(d["_id"]),
                type=d.get("type", "system"),
                title=d.get("title", ""),
                message=d.get("message", ""),
                createdAt=created_iso,
                read=bool(d.get("read", False)),
                metadata=d.get("metadata", {}),
            )
        )

    return NotificationListResponse(
        notifications=items,
        unreadCount=unread_count,
        pagination=PaginationDetails(
            limit=limit,
            offset=offset,
            total=total_matching,
        ),
    )


def mark_notification_as_read(student_id: str, notification_id: str) -> Optional[Dict[str, Any]]:
    """Mark a specific notification as read, ensuring it belongs to the authenticated student.

    Args:
        student_id: Authenticated student ID.
        notification_id: String MongoDB ObjectId.

    Returns:
        Dict with {"id": notification_id, "read": True} or None if not found / unauthorized.
    """
    try:
        oid = ObjectId(notification_id)
    except InvalidId:
        return None

    try:
        res = db_manager.notifications.find_one_and_update(
            filter={"_id": oid, "studentId": student_id},
            update={"$set": {"read": True}},
            return_document=ReturnDocument.AFTER,
        )
        if not res:
            return None
        return {"id": str(res["_id"]), "read": True}
    except PyMongoError as exc:
        logger.error("Database error marking notification %s read: %s", notification_id, exc)
        return None


def mark_all_notifications_as_read(student_id: str) -> int:
    """Mark all unread notifications for the authenticated student as read.

    Args:
        student_id: Authenticated student ID.

    Returns:
        Count of updated notifications.
    """
    try:
        res = db_manager.notifications.update_many(
            filter={"studentId": student_id, "read": False},
            update={"$set": {"read": True}},
        )
        logger.info("Marked %d notifications as read for student %s", res.modified_count, student_id)
        return res.modified_count
    except PyMongoError as exc:
        logger.error("Database error marking all notifications read for %s: %s", student_id, exc)
        return 0
