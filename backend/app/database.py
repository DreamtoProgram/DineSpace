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
        self._mock_db: Optional[Any] = None
        self._is_connected: bool = False
        self._last_failure_time: float = 0.0
        self._circuit_breaker_cooldown: float = 60.0  # seconds to skip reconnect after failure

    def _init_mock_db(self) -> None:
        """Initialize and pre-seed in-memory mock MongoDB database when real MongoDB is unavailable."""
        if self._mock_db is not None:
            self.db = self._mock_db
            return

        try:
            import mongomock
            settings = get_settings()
            mock_client = mongomock.MongoClient()
            mock_db = mock_client[settings.MONGODB_DATABASE]

            # Pre-seed demo students
            from app.services.auth_service import DEMO_STUDENTS
            for student in DEMO_STUDENTS.values():
                mock_db["students"].update_one(
                    {"studentId": student["studentId"]},
                    {"$set": dict(student)},
                    upsert=True,
                )

            # Pre-seed initial occupied seats
            initial_occupied = [3, 7, 12, 18, 25, 31, 34, 42, 51, 58, 64, 71, 77, 85, 92]
            for seat in initial_occupied:
                mock_db["occupancy"].update_one(
                    {"seatNumber": seat, "diningHall": "Central Mess"},
                    {
                        "$set": {
                            "seatNumber": seat,
                            "studentId": f"STU{1000+seat}",
                            "diningHall": "Central Mess",
                            "entryTime": "2026-11-20T12:00:00+05:30",
                            "exitTime": None,
                            "status": "occupied",
                            "mealType": "Lunch",
                        }
                    },
                    upsert=True,
                )

            self._mock_db = mock_db
            self.db = mock_db
            logger.info("Initialized and pre-seeded in-memory mock store for zero-delay operations.")
        except Exception as exc:
            logger.warning("Could not initialize mock db: %s", exc)

    def connect(self, force: bool = False) -> None:
        """Initialize MongoDB client and test connectivity with circuit-breaker."""
        import os
        import time

        now = time.time()
        # If recently failed and not forced, skip connection attempt to prevent blocking delays
        if not force and not self._is_connected and (now - self._last_failure_time < self._circuit_breaker_cooldown):
            if self.db is None:
                self._init_mock_db()
            return

        settings = get_settings()
        self._is_connected = False

        # If default localhost and in serverless cloud (e.g. Vercel), failover immediately without blocking
        if "localhost" in settings.MONGODB_URI and (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")):
            self._last_failure_time = now
            logger.info("Serverless cloud environment detected with localhost URI. Operating in zero-delay fast demo store mode.")
            self._init_mock_db()
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
            self._init_mock_db()
            logger.warning(
                "MongoDB connection ping failed at %s. Error: %s. "
                "Running in resilient mock store mode.",
                settings.MONGODB_URI,
                exc,
            )

    @property
    def is_connected(self) -> bool:
        """Return True if connection to MongoDB was verified and active or mock store is available."""
        return self.db is not None

    def close(self) -> None:
        """Close the MongoDB connection pool."""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            self._mock_db = None
            logger.info("Closed MongoDB connection.")

    def ping(self) -> bool:
        """Check if MongoDB server is currently reachable."""
        if self.client is None:
            return self.db is not None
        try:
            self.client.admin.command("ping")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError):
            return self.db is not None

    def get_database(self) -> Database:
        """Retrieve the database instance, reconnecting if necessary."""
        if self.db is None:
            self.connect()
        if self.db is None:
            self._init_mock_db()
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
