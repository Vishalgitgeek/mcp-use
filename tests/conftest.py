"""Pytest configuration and fixtures."""
import pytest
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Set test environment variables
os.environ["AGENT_API_KEY"] = "test-api-key"
os.environ["COMPOSIO_API_KEY"] = "test-composio-key"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["OAUTH_REDIRECT_BASE"] = "https://mcp.openanalyst.com"


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key"


@pytest.fixture
def headers(api_key):
    """Request headers with API key."""
    return {"X-API-Key": api_key}


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB collection."""
    with patch('mcp_service.db.mongodb.get_collection') as mock:
        collection = MagicMock()
        collection.find_one = AsyncMock(return_value=None)
        collection.find = MagicMock()
        collection.insert_one = AsyncMock()
        collection.update_one = AsyncMock()
        collection.delete_one = AsyncMock()
        collection.find_one_and_delete = AsyncMock()
        mock.return_value = collection
        yield collection


@pytest.fixture
def mock_composio_service():
    """Mock Composio service."""
    with patch('mcp_service.services.composio_service.ComposioService') as mock:
        service = MagicMock()
        service.initiate_connection = MagicMock(return_value={
            "auth_url": "https://composio.dev/auth/gmail",
            "connection_id": "test-connection-123",
            "status": "pending"
        })
        service.get_connection = MagicMock(return_value=None)
        service.get_tools = MagicMock(return_value=[])
        mock.return_value = service
        yield service


@pytest.fixture
def sample_oauth_session():
    """Sample OAuth session data."""
    from datetime import datetime
    return {
        "session_id": "test-session-uuid",
        "redirect_url": "https://myapp.com/oauth/callback",
        "user_id": "user123",
        "provider": "gmail",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def sample_integration():
    """Sample integration data."""
    from datetime import datetime
    return {
        "_id": "integration123",
        "user_id": "user123",
        "provider": "gmail",
        "status": "active",
        "composio_entity_id": "user_user123",
        "composio_connection_id": "conn123",
        "connected_email": "user@gmail.com",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
