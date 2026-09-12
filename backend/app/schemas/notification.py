from typing import Any, Dict, List
from pydantic import BaseModel, Field

from app.schemas.visit import PaginationDetails


class NotificationItem(BaseModel):
    """Notification item detail for client presentation."""

    id: str = Field(..., description="Unique notification identifier")
    type: str = Field(..., description="Category: 'menu', 'crowd', 'visit', or 'system'")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message body")
    createdAt: str = Field(..., description="Timezone-aware ISO 8601 creation timestamp")
    read: bool = Field(default=False, description="Whether the notification has been read")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional contextual payload (seatNumber, exitReason, etc.)",
    )


class NotificationListResponse(BaseModel):
    """Response schema for listing student notifications."""

    notifications: List[NotificationItem] = Field(
        default_factory=list,
        description="List of notifications, newest first",
    )
    unreadCount: int = Field(..., description="Total unread notifications across all categories")
    pagination: PaginationDetails = Field(..., description="Pagination metadata")


class NotificationReadStatus(BaseModel):
    """Minimal status confirmation for a single read notification."""

    id: str = Field(..., description="Notification ID that was marked read")
    read: bool = Field(default=True, description="Updated read status")


class NotificationReadResponse(BaseModel):
    """Response schema upon marking a single notification as read."""

    success: bool = Field(default=True, description="Indicates operation success")
    notification: NotificationReadStatus = Field(..., description="Notification read status details")


class NotificationReadAllResponse(BaseModel):
    """Response schema upon marking all notifications as read."""

    success: bool = Field(default=True, description="Indicates operation success")
    updatedCount: int = Field(..., description="Number of notifications marked as read")
