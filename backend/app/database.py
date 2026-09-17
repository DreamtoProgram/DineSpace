import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages the MongoDB connection pool and provides clean access to collections."""

    def __init__(self) -> None:
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._is_connected: bool = False
        self._last_failure_time: float = 0.0
        self._circuit_breaker_cooldown: float = 60.0  # seconds to skip reconnect after failure

    def connect(self, force: bool = False) -> None:
        """Initialize MongoDB client and test connectivity with circuit-breaker."""
        import os
        import time

        now = time.time()
        # If recently failed and not forced, skip connection attempt to prevent blocking delays
        if not force and not self._is_connected and (now - self._last_failure_time < self._circuit_breaker_cooldown):
            return

        settings = get_settings()
        self._is_connected = False

        # If default localhost and in serverless cloud (e.g. Vercel), failover immediately without blocking
        if "localhost" in settings.MONGODB_URI and (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")):
            self._last_failure_time = now
            logger.info("Serverless cloud environment detected with localhost URI. Operating in zero-delay fast demo store mode.")
            return

        try:
            self.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            )
            # Support database name specified in connection URI (e.g. Atlas mongodb+srv://.../dinespace)
            try:
                self.db = self.client.get_default_database()
            except Exception:
                self.db = None

            if self.db is None:
                self.db = self.client[settings.MONGODB_DATABASE]

            # Ping database to verify connection immediately
            self.client.admin.command("ping")
            self._is_connected = True
            self._last_failure_time = 0.0
            logger.info(
                "Successfully connected to MongoDB database '%s' at %s",
                self.db.name,
                settings.MONGODB_URI,
            )
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as exc:
            self._is_connected = False
            self._last_failure_time = now
            self.client = None
            self.db = None
            logger.warning(
                "MongoDB connection ping failed at %s. Error: %s. "
                "Running in resilient demo/fallback mode (cooldown active).",
                settings.MONGODB_URI,
                exc,
            )

    @property
    def is_connected(self) -> bool:
        """Return True if connection to MongoDB was verified and active."""
        return getattr(self, "_is_connected", False) or (self.db is not None and self.client is not None)

    def close(self) -> None:
        """Close the MongoDB connection pool."""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Closed MongoDB connection.")

    def ping(self) -> bool:
        """Check if MongoDB server is currently reachable."""
        if self.client is None:
            return False
        try:
            self.client.admin.command("ping")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError):
            return False

    def get_database(self) -> Database:
        """Retrieve the database instance, reconnecting if necessary."""
        if self.db is None:
            self.connect()
        return self.db

    @property
    def students(self) -> Collection:
        """Access the 'students' collection."""
        return self.get_database()["students"]

    @property
    def occupancy(self) -> Collection:
        """Access the 'occupancy' collection."""
        return self.get_database()["occupancy"]

    @property
    def menu(self) -> Collection:
        """Access the 'menu' collection."""
        return self.get_database()["menu"]

    @property
    def notifications(self) -> Collection:
        """Access the 'notifications' collection."""
        return self.get_database()["notifications"]


db_manager = DatabaseManager()


def get_db() -> Database:
    """Dependency helper to get the database instance."""
    return db_manager.get_database()
