from typing import Optional, Union
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.menu import DayMenusResponse, MealMenu, MealType, SingleMenuResponse
from app.services.menu_service import (
    get_menu_for_date_and_meal,
    get_menus_for_date,
    get_today_date_str,
    validate_date_format,
)

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get(
    "/today",
    response_model=DayMenusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Today's Menu",
    description="Retrieve all available meals (Lunch, Dinner) scheduled for today in the local campus timezone.",
    responses={
        200: {"description": "Today's dining menu retrieved successfully."},
        404: {"description": "No menu found for today."},
    },
)
def get_today_menu() -> DayMenusResponse:
    """Fetch all meal menus for today's date."""
    today = get_today_date_str()
    menus = get_menus_for_date(today)

    if not menus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No dining menu found for today ({today}).",
        )

    return DayMenusResponse(
        date=today,
        menus=[
            MealMenu(
                mealType=m["mealType"],
                items=m.get("items", []),
            )
            for m in menus
        ],
    )


@router.get(
    "",
    response_model=Union[SingleMenuResponse, DayMenusResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Menu by Date and Meal Type",
    description="Query menu by date (YYYY-MM-DD) and optional meal type (Lunch, Dinner). Returns matching single meal or full day menu.",
    responses={
        200: {"description": "Matching menu data retrieved."},
        404: {"description": "No menu found matching criteria."},
        422: {"description": "Invalid date format or unsupported meal type."},
    },
)
def get_menu(
    date: Optional[str] = Query(
        None,
        description="Date in YYYY-MM-DD format. Defaults to today if omitted.",
        examples=["2026-09-12"],
    ),
    mealType: Optional[MealType] = Query(
        None,
        description="Filter by specific meal type: 'Lunch' or 'Dinner'.",
        examples=[MealType.LUNCH],
    ),
) -> Union[SingleMenuResponse, DayMenusResponse]:
    """Retrieve menu information filtered by date and optional meal category."""
    target_date = get_today_date_str() if date is None else validate_date_format(date)

    if mealType is not None:
        single_menu = get_menu_for_date_and_meal(target_date, mealType.value)
        if not single_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No {mealType.value} menu found for date '{target_date}'.",
            )
        return SingleMenuResponse(
            date=target_date,
            mealType=single_menu["mealType"],
            items=single_menu.get("items", []),
        )

    all_menus = get_menus_for_date(target_date)
    if not all_menus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No menus found for date '{target_date}'.",
        )

    return DayMenusResponse(
        date=target_date,
        menus=[
            MealMenu(
                mealType=m["mealType"],
                items=m.get("items", []),
            )
            for m in all_menus
        ],
    )
