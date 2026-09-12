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

    def connect(self) -> None:
        """Initialize MongoDB client and test connectivity."""
        settings = get_settings()
        try:
            self.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            )
            self.db = self.client[settings.MONGODB_DATABASE]
            # Ping database to verify connection immediately
            self.client.admin.command("ping")
            logger.info(
                "Successfully connected to MongoDB database '%s' at %s",
                settings.MONGODB_DATABASE,
                settings.MONGODB_URI,
            )
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            logger.warning(
                "MongoDB connection ping failed at %s. Error: %s. "
                "Database operations will be unavailable until MongoDB is running.",
                settings.MONGODB_URI,
                exc,
            )

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
