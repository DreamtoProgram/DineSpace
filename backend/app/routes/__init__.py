"""API routes package."""

from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.health import router as health_router
from app.routes.menu import router as menu_router
from app.routes.scan import router as scan_router
from app.routes.status import router as status_router
from app.routes.visits import router as visits_router

__all__ = [
    "admin_router",
    "auth_router",
    "health_router",
    "menu_router",
    "scan_router",
    "status_router",
    "visits_router",
]
