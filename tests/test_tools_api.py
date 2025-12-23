"""Tests for Tools API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import os

# Set test environment variables before importing app
os.environ["AGENT_API_KEY"] = "test-api-key"
os.environ["COMPOSIO_API_KEY"] = "test-composio-key"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"

from mcp_service.main import app

client = TestClient(app)
API_KEY = "test-api-key"
HEADERS = {"X-API-Key": API_KEY}


class TestHealthCheck:
    """Tests for GET /api/tools/health"""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/tools/health", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestListProviderActions:
    """Tests for GET /api/tools/actions/{provider}"""

    def test_list_actions_requires_api_key(self):
        """Test that API key is required."""
        response = client.get("/api/tools/actions/gmail")
        assert response.status_code in [401, 403, 422]

    def test_list_gmail_actions_without_schema(self):
        """Test listing Gmail actions without schema."""
        response = client.get(
            "/api/tools/actions/gmail?include_schema=false",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "gmail"
        assert "actions" in data
        assert data["schema_included"] == False

    def test_list_slack_actions(self):
        """Test listing Slack actions."""
        response = client.get(
            "/api/tools/actions/slack?include_schema=false",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "slack"

    def test_list_googledocs_actions(self):
        """Test listing Google Docs actions (alias)."""
        response = client.get(
            "/api/tools/actions/googledocs?include_schema=false",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "googledocs"

    def test_list_unknown_provider_returns_404(self):
        """Test that unknown provider returns 404."""
        response = client.get(
            "/api/tools/actions/unknown_provider",
            headers=HEADERS
        )
        assert response.status_code == 404
        assert "Unknown provider" in response.json()["detail"]

    @patch('requests.get')
    def test_list_actions_with_schema_calls_composio(self, mock_get):
        """Test listing actions with schema calls Composio API."""
        # Mock Composio API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "name": "GMAIL_SEND_EMAIL",
                    "description": "Send an email",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        response = client.get(
            "/api/tools/actions/gmail?include_schema=true",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["schema_included"] == True


class TestGetActionSchema:
    """Tests for GET /api/tools/schema/{action}"""

    def test_get_schema_requires_api_key(self):
        """Test that API key is required."""
        response = client.get(
            "/api/tools/schema/GMAIL_SEND_EMAIL"
        )
        # 422 = missing required header, 401/403 = invalid key
        assert response.status_code in [401, 403, 422]

    @patch('requests.get')
    def test_get_schema_returns_action_details(self, mock_get):
        """Test that schema endpoint returns action details."""
        # Mock Composio API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "name": "GMAIL_SEND_EMAIL",
                    "description": "Send an email via Gmail",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        response = client.get(
            "/api/tools/schema/GMAIL_SEND_EMAIL",
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "GMAIL_SEND_EMAIL"
        assert "description" in data
        assert "parameters" in data


class TestListUserTools:
    """Tests for GET /api/tools"""

    def test_list_tools_requires_user_id(self):
        """Test that user_id is required."""
        response = client.get("/api/tools", headers=HEADERS)
        assert response.status_code == 422  # Validation error

    def test_list_tools_requires_api_key(self):
        """Test that API key is required."""
        response = client.get("/api/tools?user_id=test123")
        # 422 = missing required header, 401/403 = invalid key
        assert response.status_code in [401, 403, 422]


class TestExecuteTool:
    """Tests for POST /api/tools/execute"""

    def test_execute_requires_api_key(self):
        """Test that API key is required."""
        response = client.post(
            "/api/tools/execute",
            json={
                "user_id": "test123",
                "action": "GMAIL_SEND_EMAIL",
                "params": {}
            }
        )
        # 422 = missing required header, 401/403 = invalid key
        assert response.status_code in [401, 403, 422]

    def test_execute_validates_request_body(self):
        """Test request body validation."""
        response = client.post(
            "/api/tools/execute",
            headers=HEADERS,
            json={}  # Missing required fields
        )
        assert response.status_code == 422
