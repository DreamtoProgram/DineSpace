from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, List, Optional
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # type: ignore

from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from app.config import get_settings
from app.database import db_manager

logger = logging.getLogger(__name__)

# Indian Standard Time fallback (UTC+05:30)
IST_TIMEZONE = timezone(timedelta(hours=5, minutes=30))


def get_campus_timezone() -> timezone:
    """Resolve the campus timezone from configuration, defaulting to Indian Standard Time (UTC+05:30)."""
    settings = get_settings()
    tz_str = settings.TIMEZONE

    if tz_str in ("Asia/Kolkata", "Asia/Calcutta", "IST"):
        return IST_TIMEZONE

    if ZoneInfo is not None:
        try:
            return ZoneInfo(tz_str)
        except Exception:
            logger.warning("Could not load timezone '%s', falling back to IST (UTC+05:30)", tz_str)

    return IST_TIMEZONE


def get_today_date_str() -> str:
    """Return today's date formatted as YYYY-MM-DD in the campus timezone."""
    tz = get_campus_timezone()
    return datetime.now(tz).strftime("%Y-%m-%d")


def validate_date_format(date_str: str) -> str:
    """Validate that date_str is a valid real-world calendar date in YYYY-MM-DD format.

    Args:
        date_str: String date representation.

    Returns:
        The validated date string.

    Raises:
        HTTPException(422): If format or calendar date is invalid (e.g. 2026-99-99).
    """
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date '{date_str}'. Expected valid calendar date in YYYY-MM-DD format.",
        )


def ensure_menu_indexes() -> None:
    """Ensure compound unique index on (date, mealType) exists in MongoDB menu collection."""
    try:
        db_manager.menu.create_index([("date", 1), ("mealType", 1)], unique=True)
        logger.info("Ensured compound unique index on menu (date, mealType)")
    except PyMongoError as exc:
        logger.warning("Could not ensure index on menu: %s", exc)


DEFAULT_LUNCH_ITEMS = [
    {"name": "Paneer Butter Masala", "description": "Rich tomato and butter gravy with fresh cottage cheese", "category": "Mains", "dietary": "Vegetarian", "calories": 320},
    {"name": "Dal Tadka", "description": "Protein-rich yellow lentils tempered with garlic and cumin", "category": "Mains", "dietary": "Vegetarian", "calories": 180},
    {"name": "Steamed Rice", "description": "Light, fragrant steamed basmati rice", "category": "Staples", "dietary": "Vegan", "calories": 210},
    {"name": "Fresh Roti", "description": "Freshly puffed whole wheat flatbread", "category": "Breads", "dietary": "Vegetarian", "calories": 110},
    {"name": "Gulab Jamun", "description": "Warm milk dumplings in saffron rose syrup", "category": "Dessert", "dietary": "Vegetarian", "calories": 250},
]

DEFAULT_DINNER_ITEMS = [
    {"name": "Shahi Paneer", "description": "Rich and aromatic cottage cheese gravy", "category": "Mains", "dietary": "Vegetarian", "calories": 340},
    {"name": "Mixed Dal Tadka", "description": "Slow-cooked savory lentils", "category": "Mains", "dietary": "Vegetarian", "calories": 190},
    {"name": "Jeera Rice", "description": "Fragrant cumin tempered basmati rice", "category": "Staples", "dietary": "Vegan", "calories": 220},
    {"name": "Butter Naan", "description": "Crispy and soft tandoor-baked flatbread", "category": "Breads", "dietary": "Vegetarian", "calories": 160},
    {"name": "Rasgulla", "description": "Traditional sweet cottage cheese dumplings", "category": "Dessert", "dietary": "Vegetarian", "calories": 220},
]


def get_menus_for_date(date_str: str) -> List[Dict[str, Any]]:
    """Retrieve all menus scheduled for a specific date (Lunch and Dinner).

    Args:
        date_str: Date formatted as YYYY-MM-DD.

    Returns:
        List of menu documents for the date.
    """
    validate_date_format(date_str)
    try:
        cursor = db_manager.menu.find({"date": date_str}, {"_id": 0})
        menus = list(cursor)
        meal_order = {"Lunch": 0, "Dinner": 1}
        menus.sort(key=lambda m: meal_order.get(m.get("mealType", ""), 99))
        return menus
    except (PyMongoError, Exception) as exc:
        logger.warning("Database error retrieving menus for date %s: %s. Using fallback menu schedule.", date_str, exc)
        return [
            {"date": date_str, "mealType": "Lunch", "diningHall": "Central Mess", "items": DEFAULT_LUNCH_ITEMS},
            {"date": date_str, "mealType": "Dinner", "diningHall": "Central Mess", "items": DEFAULT_DINNER_ITEMS},
        ]


def get_menu_for_date_and_meal(date_str: str, meal_type: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single menu for a specific date and meal type.

    Args:
        date_str: Date formatted as YYYY-MM-DD.
        meal_type: Meal type string (Lunch, Dinner).

    Returns:
        Menu document if found, None otherwise.
    """
    validate_date_format(date_str)
    try:
        return db_manager.menu.find_one(
            {"date": date_str, "mealType": meal_type},
            {"_id": 0},
        )
    except (PyMongoError, Exception) as exc:
        logger.warning(
            "Database error retrieving menu for date %s and meal %s: %s. Using default.",
            date_str,
            meal_type,
            exc,
        )
        items = DEFAULT_LUNCH_ITEMS if meal_type.lower() == "lunch" else DEFAULT_DINNER_ITEMS
        return {
            "date": date_str,
            "mealType": meal_type,
            "diningHall": "Central Mess",
            "items": items,
        }


def upsert_menu(date_str: str, meal_type: str, items: List[Dict[str, str]]) -> Dict[str, Any]:
    """Insert or update a menu document in MongoDB.

    Args:
        date_str: Date in YYYY-MM-DD format.
        meal_type: Meal category (e.g. Lunch, Dinner).
        items: List of dictionaries with 'name' and 'description'.

    Returns:
        The upserted menu record.
    """
    validate_date_format(date_str)
    record = {
        "date": date_str,
        "mealType": meal_type,
        "items": items,
    }
    try:
        db_manager.menu.update_one(
            {"date": date_str, "mealType": meal_type},
            {"$set": record},
            upsert=True,
        )
        return record
    except (PyMongoError, Exception) as exc:
        logger.warning("Failed to upsert menu for %s (%s): %s. Returning memory record.", date_str, meal_type, exc)
        return record
