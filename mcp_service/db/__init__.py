"""Database module."""
from .mongodb import get_database, get_collection, close_connection

__all__ = ["get_database", "get_collection", "close_connection"]
