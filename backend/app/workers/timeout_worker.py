import asyncio
import logging
from typing import Optional

from app.config import get_settings
from app.services.timeout_service import expire_abandoned_visits

logger = logging.getLogger(__name__)


class TimeoutSweeperWorker:
    """Background asyncio worker that periodically expires abandoned dining visits.

    Runs on a configurable interval (default: 60s), invoking the database expiration service
    via asyncio.to_thread to prevent blocking the asynchronous FastAPI event loop.
    """

    def __init__(self, interval_seconds: Optional[int] = None):
        settings = get_settings()
        self.interval_seconds = (
            interval_seconds if interval_seconds is not None else settings.SWEEPER_INTERVAL_SECONDS
        )
        self._task: Optional[asyncio.Task] = None
        self._running: bool = False

    @property
    def is_running(self) -> bool:
        """Check if the worker is currently running."""
        return self._running and self._task is not None and not self._task.done()

    async def _run_loop(self) -> None:
        """Periodic background loop."""
        logger.info(
            "Seat timeout sweeper worker started (interval: %d seconds)",
            self.interval_seconds,
        )
        while self._running:
            try:
                await asyncio.sleep(self.interval_seconds)
                # Execute synchronous database operations in thread pool
                count = await asyncio.to_thread(expire_abandoned_visits)
                if count > 0:
                    logger.info("Sweeper cycle completed: expired %d abandoned visit(s)", count)
            except asyncio.CancelledError:
                logger.info("Seat timeout sweeper worker task cancelled")
                break
            except Exception as exc:
                # Catch unexpected database or network errors to keep the worker alive
                logger.error("Error during seat timeout sweeper cycle: %s", exc)

    def start(self) -> None:
        """Start the background worker task."""
        if self.is_running:
            logger.warning("Seat timeout sweeper worker already running")
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name="seat_timeout_sweeper")

    async def stop(self) -> None:
        """Gracefully stop and clean up the background worker task."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            except Exception as exc:
                logger.error("Error during sweeper worker shutdown: %s", exc)
            self._task = None
            logger.info("Seat timeout sweeper worker stopped cleanly")
