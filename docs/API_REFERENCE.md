# MCP Integration Service - API Reference v2.0

## Overview

The MCP Integration Service provides a REST API for managing OAuth integrations and exposing tools to AI agents. All endpoints (except OAuth callbacks) require API key authentication.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Your Backend  │────▶│  MCP Service    │────▶│    Composio     │
│   (OA Agent)    │     │  (This API)     │     │  (OAuth + Exec) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │    MongoDB      │
                        │ (User Records)  │
                        └─────────────────┘
```

**Base URL:** `https://mcp.openanalyst.com`

---

## Authentication

All endpoints require the `X-API-Key` header:

```
X-API-Key: your_agent_api_key
```

Set `AGENT_API_KEY` in your `.env` file. This key is used by your backend/agents to authenticate.

---

## API Endpoints

### Health Check

```http
GET /api/tools/health
```

**Authentication:** None required

**Response:**
```json
{
  "status": "healthy",
  "composio": "connected"
}
```

---

## Integration Endpoints

### List Available Integrations

```http
GET /api/integrations
```

**Headers:**
- `X-API-Key` (required): Your API key

**Response:**
```json
["gmail", "slack"]
```

---

### List User's Connected Integrations

```http
GET /api/integrations/connected?user_id={user_id}
```

**Headers:**
- `X-API-Key` (required): Your API key

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | User ID from your system |

**Example:**
```bash
curl -X GET "https://mcp.openanalyst.com/api/integrations/connected?user_id=user_123" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "integrations": [
    {
      "provider": "gmail",
      "status": "active",
      "connected_email": "user@example.com",
      "connected_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Connect Integration (Initiate OAuth)

```http
POST /api/integrations/connect
```

**Headers:**
- `X-API-Key` (required): Your API key
- `Content-Type: application/json`

**Request Body:**
```json
{
  "user_id": "user_123",
  "provider": "gmail",
  "redirect_url": "https://your-app.com/oauth-complete",
  "force_reauth": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | Your system's user ID |
| provider | string | Yes | Integration provider (`gmail`, `slack`) |
| redirect_url | string | No | URL to redirect after OAuth completion |
| force_reauth | boolean | No | Force re-authentication (default: false) |

**Example:**
```bash
curl -X POST "https://mcp.openanalyst.com/api/integrations/connect" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "provider": "gmail",
    "redirect_url": "https://your-app.com/oauth-done"
  }'
```

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/oauth/...",
  "message": "Redirect user to auth_url to connect gmail"
}
```

If already connected:
```json
{
  "auth_url": null,
  "status": "already_connected",
  "message": "gmail is already connected"
}
```

---

### Disconnect Integration

```http
POST /api/integrations/disconnect
```

**Headers:**
- `X-API-Key` (required): Your API key
- `Content-Type: application/json`

**Request Body:**
```json
{
  "user_id": "user_123",
  "provider": "gmail"
}
```

**Response:**
```json
{
  "message": "gmail disconnected successfully"
}
```

---

### Get Integration Status

```http
GET /api/integrations/{provider}/status?user_id={user_id}
```

**Headers:**
- `X-API-Key` (required): Your API key

**Path Parameters:**
- `provider`: Integration provider (`gmail`, `slack`)

**Query Parameters:**
- `user_id` (required): User ID to check status for

**Response:**
```json
{
  "provider": "gmail",
  "status": "active",
  "connected_email": "user@example.com"
}
```

---

### OAuth Callback (Internal)

```http
GET /api/integrations/callback
```

This endpoint is called by Composio after OAuth completion. **No API key required.**

After OAuth, redirects to your `redirect_url` with query params:
- `?connected={provider}&status=success` on success
- `?error={error_message}` on failure

---

## Tools Endpoints

### List User's Available Tools

```http
GET /api/tools?user_id={user_id}
```

**Headers:**
- `X-API-Key` (required): Your API key

**Query Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | User ID to get tools for |

**Example:**
```bash
curl -X GET "https://mcp.openanalyst.com/api/tools?user_id=user_123" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "tools": [
    {
      "name": "GMAIL_SEND_EMAIL",
      "description": "Send an email via Gmail",
      "provider": "gmail",
      "parameters": {
        "type": "object",
        "properties": {
          "recipient_email": {"type": "string"},
          "subject": {"type": "string"},
          "body": {"type": "string"}
        },
        "required": ["recipient_email", "subject", "body"]
      }
    }
  ]
}
```

---

### Execute Tool

```http
POST /api/tools/execute
```

**Headers:**
- `X-API-Key` (required): Your API key
- `Content-Type: application/json`

**Request Body:**
```json
{
  "user_id": "user_123",
  "action": "GMAIL_SEND_EMAIL",
  "params": {
    "recipient_email": "recipient@example.com",
    "subject": "Hello",
    "body": "This is a test email"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | User ID to execute tool for |
| action | string | Yes | Action name (e.g., `GMAIL_SEND_EMAIL`) |
| params | object | Yes | Action-specific parameters |

**Success Response:**
```json
{
  "success": true,
  "result": {
    "messageId": "abc123",
    "threadId": "xyz789"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "User does not have gmail connected"
}
```

---

### List Provider Actions

```http
GET /api/tools/actions/{provider}
```

**Headers:**
- `X-API-Key` (required): Your API key

**Path Parameters:**
- `provider`: Provider name (`gmail`, `slack`)

**Response:**
```json
{
  "provider": "gmail",
  "actions": [
    {"name": "GMAIL_SEND_EMAIL", "description": "Send an email"},
    {"name": "GMAIL_FETCH_EMAILS", "description": "Fetch emails"}
  ]
}
```

---

## Available Actions

### Gmail Actions

| Action | Description | Required Parameters |
|--------|-------------|---------------------|
| `GMAIL_SEND_EMAIL` | Send an email | `recipient_email`, `subject`, `body` |
| `GMAIL_FETCH_EMAILS` | Fetch/search emails | None (optional: `query`, `max_results`) |
| `GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID` | Get specific email | `message_id` |
| `GMAIL_CREATE_EMAIL_DRAFT` | Create draft | `recipient_email`, `subject`, `body` |
| `GMAIL_LIST_LABELS` | List all labels | None |
| `GMAIL_DELETE_MESSAGE` | Delete email | `message_id` |

### Gmail Action Parameters

#### GMAIL_SEND_EMAIL
```json
{
  "recipient_email": "user@example.com",
  "subject": "Email subject",
  "body": "Email body content"
}
```

#### GMAIL_FETCH_EMAILS
```json
{
  "max_results": 10,
  "query": "from:user@example.com is:unread"
}
```

### Slack Actions

| Action | Description | Required Parameters |
|--------|-------------|---------------------|
| `SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL` | Send message | `channel`, `text` |
| `SLACK_LIST_ALL_SLACK_TEAM_CHANNELS` | List channels | None |
| `SLACK_SEARCH_MESSAGES` | Search messages | `query` |

### Slack Action Parameters

#### SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL
```json
{
  "channel": "#general",
  "text": "Hello from MCP!"
}
```

---

## Integration Flow

### 1. Connect a User's Account

```
Your Backend                    MCP Service                    Composio
    |                               |                               |
    |-- POST /connect ------------->|                               |
    |   {user_id, provider}         |                               |
    |                               |                               |
    |<-- {auth_url} ----------------|                               |
    |                               |                               |
    |-- Redirect user to auth_url --------------------------------->|
    |                               |                               |
    |                               |<-- OAuth callback ------------|
    |                               |                               |
    |<-- Redirect to your app ------|                               |
    |   ?connected=gmail            |                               |
```

### 2. Use Tools

```
Your AI Agent                   MCP Service                    Gmail/Slack
    |                               |                               |
    |-- GET /tools?user_id=xxx ---->|                               |
    |                               |                               |
    |<-- {tools: [...]} ------------|                               |
    |                               |                               |
    |-- POST /tools/execute ------->|                               |
    |   {user_id, action, params}   |-- Execute action ------------>|
    |                               |                               |
    |<-- {success, result} ---------|<-- Result --------------------|
```

---

## Complete Integration Example

```python
import requests

API_KEY = "your_agent_api_key"
BASE_URL = "https://mcp.openanalyst.com"
HEADERS = {"X-API-Key": API_KEY}

class MCPClient:
    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base
        self.headers = {"X-API-Key": api_key}

    def connect_integration(self, user_id: str, provider: str, redirect_url: str = None):
        """Initiate OAuth connection for a user."""
        resp = requests.post(
            f"{self.api_base}/api/integrations/connect",
            headers={**self.headers, "Content-Type": "application/json"},
            json={
                "user_id": user_id,
                "provider": provider,
                "redirect_url": redirect_url
            }
        )
        return resp.json()

    def get_connected(self, user_id: str):
        """Get user's connected integrations."""
        resp = requests.get(
            f"{self.api_base}/api/integrations/connected",
            params={"user_id": user_id},
            headers=self.headers
        )
        return resp.json()

    def get_tools(self, user_id: str):
        """Fetch available tools for a user."""
        resp = requests.get(
            f"{self.api_base}/api/tools",
            params={"user_id": user_id},
            headers=self.headers
        )
        return resp.json()["tools"]

    def execute(self, user_id: str, action: str, params: dict):
        """Execute a tool action."""
        resp = requests.post(
            f"{self.api_base}/api/tools/execute",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"user_id": user_id, "action": action, "params": params}
        )
        return resp.json()


# Usage Example
client = MCPClient("https://mcp.openanalyst.com", "your_api_key")

# 1. Connect Gmail for a user (redirect user to auth_url)
result = client.connect_integration("user_123", "gmail", "https://your-app.com/done")
print(f"Redirect user to: {result['auth_url']}")

# 2. After OAuth, check connected integrations
connected = client.get_connected("user_123")
print(f"Connected: {connected}")

# 3. Get available tools
tools = client.get_tools("user_123")
print(f"Available tools: {[t['name'] for t in tools]}")

# 4. Execute a tool
result = client.execute(
    "user_123",
    "GMAIL_SEND_EMAIL",
    {
        "recipient_email": "bob@example.com",
        "subject": "Hello",
        "body": "This email was sent via MCP!"
    }
)
print(f"Result: {result}")
```

---

## Error Codes

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (invalid or missing API key) |
| 404 | Not found (unknown provider or action) |
| 422 | Validation error (missing required fields) |
| 500 | Server error |

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COMPOSIO_API_KEY` | Composio API key | Yes |
| `AGENT_API_KEY` | API key for agent authentication | Yes |
| `MONGODB_URI` | MongoDB connection string | Yes |
| `MONGODB_DB_NAME` | Database name | No (default: `mcp_integrations`) |
| `MCP_SERVICE_HOST` | Service host | No (default: `0.0.0.0`) |
| `MCP_SERVICE_PORT` | Service port | No (default: `8001`) |
| `OAUTH_REDIRECT_BASE` | Base URL for OAuth redirects | Yes |

---

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python -m mcp_service.main
```

The service will be available at `http://localhost:8001`

- API docs: `http://localhost:8001/docs`
- Health check: `http://localhost:8001/api/tools/health`
