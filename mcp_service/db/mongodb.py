"""MongoDB connection management using Motor (async driver)."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from ..config import MONGODB_URI, MONGODB_DB_NAME

logger = logging.getLogger(__name__)

# Global client instance
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongodb():
    """Initialize MongoDB connection."""
    global _client, _database

    if _client is None:
        logger.info(f"Connecting to MongoDB at {MONGODB_URI}")
        _client = AsyncIOMotorClient(MONGODB_URI)
        _database = _client[MONGODB_DB_NAME]

        # Test connection
        try:
            await _client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    return _database


async def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance."""
    global _database

    if _database is None:
        await connect_to_mongodb()

    return _database


async def get_collection(collection_name: str):
    """Get a collection from the database."""
    db = await get_database()
    return db[collection_name]


async def close_connection():
    """Close MongoDB connection."""
    global _client, _database

    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")


async def create_indexes():
    """Create necessary indexes for collections."""
    db = await get_database()

    # Integrations collection indexes
    integrations = db["integrations"]

    # Unique index on user_id + provider (one account per integration per user)
    await integrations.create_index(
        [("user_id", 1), ("provider", 1)],
        unique=True,
        name="user_provider_unique"
    )

    # Index for querying by user_id
    await integrations.create_index(
        [("user_id", 1)],
        name="user_id_index"
    )

    logger.info("Database indexes created")
