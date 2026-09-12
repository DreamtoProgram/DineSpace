"""Business logic and service layer."""

from app.services.auth_service import (
    authenticate_student,
    ensure_student_indexes,
    get_student_by_id,
)
from app.services.entry_service import (
    assign_virtual_seat_and_checkin,
    check_student_active_visit,
    validate_student_pass,
)
from app.services.menu_service import (
    ensure_menu_indexes,
    get_campus_timezone,
    get_menu_for_date_and_meal,
    get_menus_for_date,
    get_today_date_str,
    upsert_menu,
    validate_date_format,
)
from app.services.occupancy_service import (
    calculate_crowd_level,
    determine_current_meal_type,
    ensure_occupancy_indexes,
    get_active_occupancy_count,
    get_occupancy_status,
)
from app.services.seat_service import get_virtual_seat_map
from app.services.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.services.settings_service import (
    change_student_password,
    get_student_settings,
    update_student_settings,
)
from app.services.visit_service import (
    calculate_visit_duration_minutes,
    get_student_current_active_visit,
)

__all__ = [
    "assign_virtual_seat_and_checkin",
    "authenticate_student",
    "calculate_crowd_level",
    "calculate_visit_duration_minutes",
    "change_student_password",
    "check_student_active_visit",
    "create_access_token",
    "decode_access_token",
    "determine_current_meal_type",
    "ensure_menu_indexes",
    "ensure_occupancy_indexes",
    "ensure_student_indexes",
    "get_active_occupancy_count",
    "get_campus_timezone",
    "get_menu_for_date_and_meal",
    "get_menus_for_date",
    "get_occupancy_status",
    "get_student_by_id",
    "get_student_current_active_visit",
    "get_student_settings",
    "get_today_date_str",
    "get_virtual_seat_map",
    "hash_password",
    "update_student_settings",
    "upsert_menu",
    "validate_date_format",
    "validate_student_pass",
    "verify_password",
]
