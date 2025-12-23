"""Tests for Integrations API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import os

# Set test environment variables before importing app
os.environ["AGENT_API_KEY"] = "test-api-key"
os.environ["COMPOSIO_API_KEY"] = "test-composio-key"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["OAUTH_REDIRECT_BASE"] = "https://mcp.openanalyst.com"

from mcp_service.main import app

client = TestClient(app)
API_KEY = "test-api-key"
HEADERS = {"X-API-Key": API_KEY}


class TestListIntegrations:
    """Tests for GET /api/integrations"""

    def test_list_available_integrations_detailed(self):
        """Test listing available integrations with details (default)."""
        response = client.get("/api/integrations", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "integrations" in data
        assert "total" in data
        assert data["total"] > 0
        # Check structure of first integration
        integration = data["integrations"][0]
        assert "provider" in integration
        assert "name" in integration
        assert "description" in integration
        assert "category" in integration
        # Check gmail is in the list
        providers = [i["provider"] for i in data["integrations"]]
        assert "gmail" in providers
        assert "slack" in providers

    def test_list_available_integrations_simple(self):
        """Test listing available integrations as simple list."""
        response = client.get("/api/integrations?detailed=false", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "gmail" in data
        assert "slack" in data

    def test_list_integrations_requires_api_key(self):
        """Test that API key is required."""
        response = client.get("/api/integrations")
        assert response.status_code in [401, 403, 422]


class TestConnectIntegration:
    """Tests for POST /api/integrations/connect"""

    def test_connect_requires_api_key(self):
        """Test that API key is required."""
        response = client.post(
            "/api/integrations/connect",
            json={
                "user_id": "test123",
                "provider": "gmail"
            }
        )
        # 422 = missing required header, 401/403 = invalid key
        assert response.status_code in [401, 403, 422]

    def test_connect_validates_provider(self):
        """Test that invalid provider returns error."""
        response = client.post(
            "/api/integrations/connect",
            headers=HEADERS,
            json={
                "user_id": "test123",
                "provider": "invalid_provider"
            }
        )
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]

    def test_connect_requires_user_id(self):
        """Test that user_id is required."""
        response = client.post(
            "/api/integrations/connect",
            headers=HEADERS,
            json={
                "provider": "gmail"
            }
        )
        assert response.status_code == 422  # Validation error


class TestOAuthCallback:
    """Tests for GET /api/integrations/callback"""

    def test_callback_success_redirects(self):
        """Test that successful callback redirects properly."""
        response = client.get(
            "/api/integrations/callback",
            params={
                "status": "success",
                "appName": "gmail",
                "connectedAccountId": "test_connection_123"
            },
            follow_redirects=False
        )
        assert response.status_code == 307  # Redirect
        assert "location" in response.headers
        location = response.headers["location"]
        assert "status=success" in location
        assert "appName=gmail" in location

    def test_callback_error_redirects_with_error(self):
        """Test that error callback includes error info."""
        response = client.get(
            "/api/integrations/callback",
            params={
                "error": "access_denied",
                "error_description": "User denied access"
            },
            follow_redirects=False
        )
        assert response.status_code == 307
        location = response.headers["location"]
        assert "error=access_denied" in location

    def test_callback_without_session_uses_default_redirect(self):
        """Test that missing session falls back to default."""
        response = client.get(
            "/api/integrations/callback",
            params={
                "status": "success",
                "appName": "gmail"
            },
            follow_redirects=False
        )
        assert response.status_code == 307
        location = response.headers["location"]
        # Should use OAUTH_REDIRECT_BASE
        assert "mcp.openanalyst.com" in location or "localhost" in location

    def test_callback_does_not_require_api_key(self):
        """Test that callback doesn't require API key (called by Composio)."""
        response = client.get(
            "/api/integrations/callback",
            params={"status": "success", "appName": "gmail"},
            follow_redirects=False
        )
        # Should not be 401/403
        assert response.status_code != 401
        assert response.status_code != 403


class TestDisconnectIntegration:
    """Tests for POST /api/integrations/disconnect"""

    def test_disconnect_requires_api_key(self):
        """Test that API key is required."""
        response = client.post(
            "/api/integrations/disconnect",
            json={
                "user_id": "test123",
                "provider": "gmail"
            }
        )
        # 422 = missing required header, 401/403 = invalid key
        assert response.status_code in [401, 403, 422]

    def test_disconnect_validates_request(self):
        """Test request validation."""
        response = client.post(
            "/api/integrations/disconnect",
            headers=HEADERS,
            json={}  # Missing required fields
        )
        assert response.status_code == 422


class TestIntegrationStatus:
    """Tests for GET /api/integrations/{provider}/status"""

    def test_status_requires_user_id(self):
        """Test that user_id is required."""
        response = client.get(
            "/api/integrations/gmail/status",
            headers=HEADERS
        )
        assert response.status_code == 422  # Validation error

    def test_status_requires_api_key(self):
        """Test that API key is required."""
        response = client.get(
            "/api/integrations/gmail/status",
            params={"user_id": "test123"}
        )
        # 422 = missing required header, 401/403 = invalid key
        assert response.status_code in [401, 403, 422]


class TestConnectedIntegrations:
    """Tests for GET /api/integrations/connected"""

    def test_connected_requires_user_id(self):
        """Test that user_id is required."""
        response = client.get(
            "/api/integrations/connected",
            headers=HEADERS
        )
        assert response.status_code == 422

    def test_connected_requires_api_key(self):
        """Test that API key is required."""
        response = client.get(
            "/api/integrations/connected",
            params={"user_id": "test123"}
        )
        # 422 = missing required header, 401/403 = invalid key
        assert response.status_code in [401, 403, 422]
