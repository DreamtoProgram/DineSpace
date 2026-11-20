from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.dependencies import require_admin
from app.schemas.admin import (
    MenuItemCreateRequest,
    MenuItemDeleteRequest,
    MenuItemUpdateRequest,
    SeatReleaseRequest,
    SeatStatusUpdateRequest,
)
from app.services.admin_service import (
    get_admin_analytics,
    get_admin_seats,
    release_seat,
    set_seat_status,
)
from app.services.menu_service import (
    add_menu_item,
    delete_menu_item,
    get_today_date_str,
    update_menu_item,
)

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get Cafeteria Live Operational Analytics",
    description="Returns real-time crowd metrics, hourly throughput, average turnaround, and active occupants.",
)
def get_analytics(
    diningHall: Optional[str] = Query(default=None, description="Dining hall facility name"),
    admin_user: Dict[str, Any] = Depends(require_admin),
) -> Dict[str, Any]:
    """Retrieve cafeteria management metrics."""
    return get_admin_analytics(dining_hall=diningHall)


@router.get(
    "/seats",
    status_code=status.HTTP_200_OK,
    summary="Get All Seats with Administrative Status",
    description="Retrieve full list of all 100 virtual seats including maintenance and reservation notes.",
)
def get_seats_admin(
    diningHall: Optional[str] = Query(default=None, description="Dining hall facility name"),
    admin_user: Dict[str, Any] = Depends(require_admin),
) -> List[Dict[str, Any]]:
    """Retrieve full seat map for staff management."""
    return get_admin_seats(dining_hall=diningHall)


@router.post(
    "/seats/status",
    status_code=status.HTTP_200_OK,
    summary="Update Seat Status (Maintenance / Reserved / Available)",
    description="Staff override to mark seats under repair, reserved for VIPs, or return them to available.",
)
def update_seat(
    payload: SeatStatusUpdateRequest,
    admin_user: Dict[str, Any] = Depends(require_admin),
) -> Dict[str, Any]:
    """Update seat operational state."""
    return set_seat_status(
        seat_number=payload.seatNumber,
        status_value=payload.status,
        note=payload.note,
        dining_hall=payload.diningHall,
    )


@router.post(
    "/seats/release",
    status_code=status.HTTP_200_OK,
    summary="Force Release Stuck or Occupied Seat",
    description="Administrative action to immediately end an active visit and free the virtual seat.",
)
def force_release(
    payload: SeatReleaseRequest,
    admin_user: Dict[str, Any] = Depends(require_admin),
) -> Dict[str, Any]:
    """Force release an occupied seat."""
    return release_seat(
        seat_number=payload.seatNumber,
        reason=payload.reason,
        dining_hall=payload.diningHall,
    )


@router.post(
    "/menu/item",
    status_code=status.HTTP_201_CREATED,
    summary="Add Menu Item",
    description="Add a new food item to the scheduled menu.",
)
def add_item_to_menu(
    payload: MenuItemCreateRequest,
    admin_user: Dict[str, Any] = Depends(require_admin),
) -> Dict[str, Any]:
    """Add a new item to today's or specified date's meal menu."""
    target_date = payload.date or get_today_date_str()
    item_dict = payload.item.model_dump()
    result = add_menu_item(target_date, payload.mealType, item_dict)
    return {
        "success": True,
        "message": f"Item '{payload.item.name}' added to {payload.mealType} menu.",
        "menu": result,
    }


@router.put(
    "/menu/item",
    status_code=status.HTTP_200_OK,
    summary="Update Menu Item",
    description="Update nutritional details or category of an existing menu item.",
)
def update_item_in_menu(
    payload: MenuItemUpdateRequest,
    admin_user: Dict[str, Any] = Depends(require_admin),
) -> Dict[str, Any]:
    """Update an item in the menu."""
    target_date = payload.date or get_today_date_str()
    item_dict = payload.item.model_dump()
    result = update_menu_item(target_date, payload.mealType, payload.itemName, item_dict)
    return {
        "success": True,
        "message": f"Item '{payload.itemName}' updated successfully.",
        "menu": result,
    }


@router.delete(
    "/menu/item",
    status_code=status.HTTP_200_OK,
    summary="Delete Menu Item",
    description="Remove an item from today's or specified date's meal menu.",
)
def delete_item_from_menu(
    payload: MenuItemDeleteRequest,
    admin_user: Dict[str, Any] = Depends(require_admin),
) -> Dict[str, Any]:
    """Remove an item from the menu."""
    target_date = payload.date or get_today_date_str()
    result = delete_menu_item(target_date, payload.mealType, payload.itemName)
    return {
        "success": True,
        "message": f"Item '{payload.itemName}' removed from {payload.mealType} menu.",
        "menu": result,
    }
