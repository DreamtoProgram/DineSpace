from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_student
from app.schemas.notification import (
    NotificationListResponse,
    NotificationReadAllResponse,
    NotificationReadResponse,
    NotificationReadStatus,
)
from app.services.notification_service import (
    get_student_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student Notifications",
    description=(
        "Retrieve notifications for the authenticated student, sorted newest first by creation timestamp. "
        "Supports filtering by category ('menu', 'crowd', 'visit', 'system', or 'all') and pagination."
    ),
    responses={
        200: {"description": "Notifications retrieved successfully."},
        400: {"description": "Invalid category filter type."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
        422: {"description": "Validation error (invalid limit or negative offset)."},
    },
)
def list_notifications(
    type: Optional[str] = Query(
        default=None,
        description="Filter by notification category: 'menu', 'crowd', 'visit', 'system', or 'all'",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of notifications to return per page (1 to 100)",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of notifications to skip for pagination",
    ),
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> NotificationListResponse:
    """List notifications for authenticated student with filtering and pagination."""
    student_id = current_student["studentId"]
    return get_student_notifications(
        student_id=student_id,
        notification_type=type,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/read-all",
    response_model=NotificationReadAllResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark All Notifications as Read",
    description="Mark all unread notifications belonging to the authenticated student as read.",
    responses={
        200: {"description": "All unread notifications marked as read."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
    },
)
def mark_all_read(
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> NotificationReadAllResponse:
    """Mark all unread notifications for authenticated student as read."""
    student_id = current_student["studentId"]
    updated_count = mark_all_notifications_as_read(student_id)
    return NotificationReadAllResponse(success=True, updatedCount=updated_count)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark Single Notification as Read",
    description="Mark a single notification belonging to the authenticated student as read.",
    responses={
        200: {"description": "Notification marked as read."},
        401: {"description": "Missing, invalid, or expired authentication token."},
        403: {"description": "Student account is inactive."},
        404: {"description": "Notification not found or belongs to another student."},
    },
)
def mark_single_read(
    notification_id: str,
    current_student: Dict[str, Any] = Depends(get_current_student),
) -> NotificationReadResponse:
    """Mark a specific notification as read."""
    student_id = current_student["studentId"]
    result = mark_notification_as_read(student_id=student_id, notification_id=notification_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )
    return NotificationReadResponse(
        success=True,
        notification=NotificationReadStatus(id=result["id"], read=result["read"]),
    )
