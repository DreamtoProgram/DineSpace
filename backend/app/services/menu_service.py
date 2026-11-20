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
    if not db_manager.is_connected:
        return
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


NORTH_HOSTEL_LUNCH_ITEMS = [
    {"name": "Amritsari Chole Kulche", "description": "Authentic spiced chickpeas served with crisp butter kulcha", "category": "Mains", "dietary": "Vegetarian", "calories": 420},
    {"name": "Dal Makhani", "description": "Slow-cooked creamy black lentils with aromatic whole spices", "category": "Mains", "dietary": "Vegetarian", "calories": 310},
    {"name": "Jeera Basmati Rice", "description": "Fragrant basmati rice tempered with roasted cumin", "category": "Rice & Breads", "dietary": "Vegan", "calories": 180},
    {"name": "Cucumber Mint Raita", "description": "Chilled yogurt seasoned with roasted cumin and fresh mint", "category": "Sides & Salads", "dietary": "Vegetarian", "calories": 95},
    {"name": "Kesar Phirni", "description": "Slow-cooked chilled saffron ground rice pudding in earthen pot", "category": "Dessert", "dietary": "Vegetarian", "calories": 210},
]

FOOD_COURT_LUNCH_ITEMS = [
    {"name": "Paneer Tikka Roll", "description": "Char-grilled cottage cheese cubes wrapped in flaky paratha", "category": "Mains", "dietary": "Vegetarian", "calories": 380},
    {"name": "Veg Hakka Noodles", "description": "Wok-tossed noodles with bell peppers, shredded cabbage and carrots", "category": "Mains", "dietary": "Vegan", "calories": 290},
    {"name": "Crispy Chilli Corn", "description": "Golden crispy sweet corn tossed with spring onions and peppers", "category": "Sides & Salads", "dietary": "Vegan", "calories": 220},
    {"name": "Cold Brew Coffee", "description": "Chilled artisanal Arabica brew with creamy milk", "category": "Beverage", "dietary": "Vegetarian", "calories": 140},
    {"name": "Chocolate Brownie", "description": "Fudgy Belgian dark chocolate brownie with walnut crunch", "category": "Dessert", "dietary": "Vegetarian", "calories": 280},
]


def get_menus_for_date(date_str: str, dining_hall: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve all menus scheduled for a specific date (Lunch and Dinner) and dining hall.

    Args:
        date_str: Date formatted as YYYY-MM-DD.
        dining_hall: Optional dining facility filter.

    Returns:
        List of menu documents for the date.
    """
    validate_date_format(date_str)
    target_hall = dining_hall or "Central Mess"

    lunch_items = DEFAULT_LUNCH_ITEMS
    dinner_items = DEFAULT_DINNER_ITEMS
    if target_hall == "North Hostel Mess":
        lunch_items = NORTH_HOSTEL_LUNCH_ITEMS
    elif target_hall == "Food Court (Student Center)":
        lunch_items = FOOD_COURT_LUNCH_ITEMS

    fallback_menus = [
        {"date": date_str, "mealType": "Lunch", "diningHall": target_hall, "items": lunch_items},
        {"date": date_str, "mealType": "Dinner", "diningHall": target_hall, "items": dinner_items},
    ]

    if not db_manager.is_connected:
        return fallback_menus

    try:
        query: Dict[str, Any] = {"date": date_str}
        if dining_hall:
            query["diningHall"] = dining_hall
        cursor = db_manager.menu.find(query, {"_id": 0})
        menus = list(cursor)
        if not menus and dining_hall and date_str == get_today_date_str():
            return fallback_menus
        meal_order = {"Lunch": 0, "Dinner": 1}
        menus.sort(key=lambda m: meal_order.get(m.get("mealType", ""), 99))
        return menus
    except (PyMongoError, Exception) as exc:
        logger.warning("Database error retrieving menus for date %s: %s. Using fallback menu schedule.", date_str, exc)
        return fallback_menus


def get_menu_for_date_and_meal(date_str: str, meal_type: str, dining_hall: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single menu for a specific date, meal type, and dining hall.

    Args:
        date_str: Date formatted as YYYY-MM-DD.
        meal_type: Meal type string (Lunch, Dinner).
        dining_hall: Optional dining facility filter.

    Returns:
        Menu document if found, None otherwise.
    """
    validate_date_format(date_str)
    target_hall = dining_hall or "Central Mess"
    items = DEFAULT_LUNCH_ITEMS if meal_type.lower() == "lunch" else DEFAULT_DINNER_ITEMS
    if target_hall == "North Hostel Mess" and meal_type.lower() == "lunch":
        items = NORTH_HOSTEL_LUNCH_ITEMS
    elif target_hall == "Food Court (Student Center)" and meal_type.lower() == "lunch":
        items = FOOD_COURT_LUNCH_ITEMS

    fallback_menu = {
        "date": date_str,
        "mealType": meal_type,
        "diningHall": target_hall,
        "items": items,
    }
    if not db_manager.is_connected:
        return fallback_menu
    try:
        query: Dict[str, Any] = {"date": date_str, "mealType": meal_type}
        if dining_hall:
            query["diningHall"] = dining_hall
        res = db_manager.menu.find_one(query, {"_id": 0})
        if not res and dining_hall and date_str == get_today_date_str():
            return fallback_menu
        return res
    except (PyMongoError, Exception) as exc:
        logger.warning(
            "Database error retrieving menu for date %s and meal %s: %s. Using default.",
            date_str,
            meal_type,
            exc,
        )
        return fallback_menu


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


def add_menu_item(date_str: str, meal_type: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new item to the menu for a given date and meal type."""
    current_menu = get_menu_for_date_and_meal(date_str, meal_type)
    items = list(current_menu.get("items", [])) if current_menu else []
    # Avoid duplicate name
    items = [i for i in items if i.get("name") != item.get("name")]
    items.append(item)
    return upsert_menu(date_str, meal_type, items)


def update_menu_item(date_str: str, meal_type: str, item_name: str, new_item: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing menu item by name."""
    current_menu = get_menu_for_date_and_meal(date_str, meal_type)
    items = list(current_menu.get("items", [])) if current_menu else []
    updated = False
    new_items = []
    for it in items:
        if it.get("name") == item_name:
            new_items.append(new_item)
            updated = True
        else:
            new_items.append(it)
    if not updated:
        new_items.append(new_item)
    return upsert_menu(date_str, meal_type, new_items)


def delete_menu_item(date_str: str, meal_type: str, item_name: str) -> Dict[str, Any]:
    """Remove a menu item by name."""
    current_menu = get_menu_for_date_and_meal(date_str, meal_type)
    items = list(current_menu.get("items", [])) if current_menu else []
    filtered_items = [i for i in items if i.get("name") != item_name]
    return upsert_menu(date_str, meal_type, filtered_items)

