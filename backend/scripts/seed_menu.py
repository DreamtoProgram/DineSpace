"""Seed script to populate demo dining menus into MongoDB.

DEMO MENU SCHEDULE:
-------------------
Today's Lunch:
- Paneer Butter Masala: A classic favorite
- Dal Tadka: Protein rich and wholesome
- Steamed Rice: Light and healthy
- Roti: Freshly made
- Gulab Jamun: Because every meal deserves a sweet ending

Today's Dinner:
- Shahi Paneer: Rich and aromatic cottage cheese gravy
- Mixed Dal Tadka: Slow-cooked savory lentils
- Jeera Rice: Fragrant cumin tempered basmati rice
- Butter Naan: Crispy and soft tandoor-baked flatbread
- Rasgulla: Traditional sweet cottage cheese dumplings
"""

import logging
import sys
from pymongo.errors import PyMongoError

from app.database import db_manager
from app.services.menu_service import ensure_menu_indexes, get_today_date_str

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_menu")

LUNCH_ITEMS = [
    {"name": "Paneer Butter Masala", "description": "A classic favorite"},
    {"name": "Dal Tadka", "description": "Protein rich and wholesome"},
    {"name": "Steamed Rice", "description": "Light and healthy"},
    {"name": "Roti", "description": "Freshly made"},
    {"name": "Gulab Jamun", "description": "Because every meal deserves a sweet ending"},
]

DINNER_ITEMS = [
    {"name": "Shahi Paneer", "description": "Rich and aromatic cottage cheese gravy"},
    {"name": "Mixed Dal Tadka", "description": "Slow-cooked savory lentils"},
    {"name": "Jeera Rice", "description": "Fragrant cumin tempered basmati rice"},
    {"name": "Butter Naan", "description": "Crispy and soft tandoor-baked flatbread"},
    {"name": "Rasgulla", "description": "Traditional sweet cottage cheese dumplings"},
]


def seed(date_str: str = "") -> None:
    """Seed demo lunch and dinner menus into MongoDB for the specified or current campus date."""
    logger.info("Connecting to MongoDB...")
    db_manager.connect()

    if not db_manager.ping():
        logger.error("Cannot connect to MongoDB. Please ensure MongoDB is running or configure MONGODB_URI.")
        sys.exit(1)

    # Ensure index on date and mealType
    ensure_menu_indexes()

    target_date = date_str if date_str else get_today_date_str()
    logger.info("Seeding menus for date: %s", target_date)

    menu_col = db_manager.menu

    meals_to_seed = [
        {"date": target_date, "mealType": "Lunch", "items": LUNCH_ITEMS},
        {"date": target_date, "mealType": "Dinner", "items": DINNER_ITEMS},
    ]

    for meal in meals_to_seed:
        menu_col.update_one(
            {"date": meal["date"], "mealType": meal["mealType"]},
            {"$set": meal},
            upsert=True,
        )
        logger.info("Seeded %s menu for %s (%d items)", meal["mealType"], meal["date"], len(meal["items"]))

    logger.info("Menu seeding completed successfully for %s.", target_date)


if __name__ == "__main__":
    custom_date = sys.argv[1] if len(sys.argv) > 1 else ""
    seed(custom_date)
