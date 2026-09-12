import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import db_manager
from app.routes.auth import router as auth_router
from app.routes.health import router as health_router
from app.routes.menu import router as menu_router
from app.routes.notifications import router as notifications_router
from app.routes.scan import router as scan_router
from app.routes.seats import router as seats_router
from app.routes.settings import router as settings_router
from app.routes.status import router as status_router
from app.routes.visits import router as visits_router
from app.services.auth_service import ensure_student_indexes
from app.services.menu_service import ensure_menu_indexes
from app.services.notification_service import ensure_notification_indexes
from app.services.occupancy_service import ensure_occupancy_indexes
from app.workers import TimeoutSweeperWorker

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dinespace")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events."""
    logger.info("Starting up DineSpace Backend...")
    # Initialize MongoDB connection pool
    db_manager.connect()
    # Ensure database indexes
    ensure_student_indexes()
    ensure_menu_indexes()
    ensure_occupancy_indexes()
    ensure_notification_indexes()
    # Start periodic seat timeout sweeper background worker
    sweeper = TimeoutSweeperWorker()
    sweeper.start()
    try:
        yield
    finally:
        logger.info("Shutting down DineSpace Backend...")
        await sweeper.stop()
        db_manager.close()



settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Campus dining management API with live crowd tracking, seat allocation, and authentication.",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle custom HTTP exceptions with consistent JSON format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled internal exceptions."""
    logger.exception("Unhandled server error processing request to %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred."},
    )


# Register API routes
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(menu_router, prefix=settings.API_V1_PREFIX)
app.include_router(status_router, prefix=settings.API_V1_PREFIX)
app.include_router(scan_router, prefix=settings.API_V1_PREFIX)
app.include_router(seats_router, prefix=settings.API_V1_PREFIX)
app.include_router(visits_router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications_router, prefix=settings.API_V1_PREFIX)
app.include_router(settings_router, prefix=settings.API_V1_PREFIX)

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

