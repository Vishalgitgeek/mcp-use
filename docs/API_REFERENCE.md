# MCP Integration Service - Developer Documentation

## Overview

The MCP Integration Service provides a unified API for AI agents to execute actions on behalf of users across multiple platforms (Gmail, Slack, etc.) using OAuth-based authentication managed by Composio.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Your AI Agent │────▶│  MCP Service    │────▶│    Composio     │
│                 │     │  (This API)     │     │  (OAuth + Exec) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │    MongoDB      │
                        │ (User Records)  │
                        └─────────────────┘
```

## Base URL

```
http://localhost:8001
```

## Authentication

### Two Authentication Methods

| Method | Header | Used For |
|--------|--------|----------|
| JWT Token | `Authorization: Bearer <token>` | User UI operations |
| API Key | `X-API-Key: <key>` | AI Agent operations |

### Getting API Key

Set `AGENT_API_KEY` in your `.env` file. This key is used by AI agents to authenticate.

```bash
AGENT_API_KEY=your_secure_api_key_here
```

---

## API Endpoints

### 1. Health Check

Check if the service is running.

```
GET /api/tools/health
```

**Authentication:** None required

**Response:**
```json
{
  "status": "healthy",
  "service": "mcp-integration-service"
}
```

---

### 2. List User Tools

Get available tools for a specific user based on their connected integrations.

```
GET /api/tools?user_id={user_id}
```

**Authentication:** `X-API-Key` header

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | Yes | The user's ID (from Google OAuth) |

**Example Request:**
```bash
curl -X GET "http://localhost:8001/api/tools?user_id=110610502660943882433" \
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

### 3. Execute Tool

Execute an action on behalf of a user.

```
POST /api/tools/execute
```

**Authentication:** `X-API-Key` header

**Request Body:**
```json
{
  "user_id": "110610502660943882433",
  "action": "GMAIL_SEND_EMAIL",
  "params": {
    "recipient_email": "recipient@example.com",
    "subject": "Hello",
    "body": "This is a test email"
  }
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | string | Yes | The user's ID |
| action | string | Yes | Action name (e.g., `GMAIL_SEND_EMAIL`) |
| params | object | Yes | Action-specific parameters |

**Example Request:**
```bash
curl -X POST "http://localhost:8001/api/tools/execute" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "110610502660943882433",
    "action": "GMAIL_SEND_EMAIL",
    "params": {
      "recipient_email": "test@example.com",
      "subject": "Test",
      "body": "Hello from MCP!"
    }
  }'
```

**Success Response:**
```json
{
  "success": true,
  "result": {
    "id": "18c5f5d1a2b3c4d5",
    "threadId": "18c5f5d1a2b3c4d5"
  },
  "error": null
}
```

**Error Response:**
```json
{
  "success": false,
  "result": null,
  "error": "User does not have gmail connected"
}
```

---

### 4. List Provider Actions

Get available actions for a specific provider.

```
GET /api/tools/actions/{provider}
```

**Authentication:** `X-API-Key` header

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| provider | string | Yes | Provider name (`gmail`, `slack`) |

**Example Request:**
```bash
curl -X GET "http://localhost:8001/api/tools/actions/gmail" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "provider": "gmail",
  "actions": [
    {"name": "GMAIL_SEND_EMAIL", "description": "Send an email"},
    {"name": "GMAIL_FETCH_EMAILS", "description": "Fetch/search emails with optional query filter"},
    {"name": "GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID", "description": "Get a specific email by message ID"},
    {"name": "GMAIL_CREATE_EMAIL_DRAFT", "description": "Create an email draft"}
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
| `GMAIL_FETCH_MESSAGE_BY_THREAD_ID` | Get thread messages | `thread_id` |
| `GMAIL_CREATE_EMAIL_DRAFT` | Create draft | `recipient_email`, `subject`, `body` |
| `GMAIL_ADD_LABEL_TO_EMAIL` | Modify labels | `message_id` |
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
  "query": "from:user@example.com is:unread",
  "label_ids": ["INBOX", "UNREAD"],
  "include_spam_trash": false
}
```

#### GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID
```json
{
  "message_id": "18c5f5d1a2b3c4d5",
  "format": "full"
}
```

### Slack Actions

| Action | Description | Required Parameters |
|--------|-------------|---------------------|
| `SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL` | Send message | `channel`, `text` |
| `SLACK_LIST_ALL_SLACK_TEAM_CHANNELS_WITH_PAGINATION` | List channels | None |
| `SLACK_FETCHES_CONVERSATION_HISTORY` | Get channel history | `channel` |
| `SLACK_SEARCH_MESSAGES_IN_SLACK` | Search messages | `query` |

### Slack Action Parameters

#### SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL
```json
{
  "channel": "#general",
  "text": "Hello from MCP!"
}
```

---

## User Management Endpoints

### 5. List User Integrations

Get all integrations for the authenticated user.

```
GET /api/integrations
```

**Authentication:** `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "integrations": [
    {
      "provider": "gmail",
      "status": "active",
      "connected_email": "user@gmail.com",
      "connected_at": "2024-01-15T10:30:00Z"
    },
    {
      "provider": "slack",
      "status": "pending",
      "connected_email": null,
      "connected_at": null
    }
  ]
}
```

### 6. Connect Integration

Initiate OAuth flow for a provider.

```
POST /api/integrations/connect
```

**Authentication:** `Authorization: Bearer <jwt_token>`

**Request Body:**
```json
{
  "provider": "gmail",
  "force_reauth": false
}
```

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "message": "Redirect user to auth_url to complete connection"
}
```

### 7. Disconnect Integration

Remove an integration connection.

```
DELETE /api/integrations/{provider}
```

**Authentication:** `Authorization: Bearer <jwt_token>`

**Response:**
```json
{
  "message": "Successfully disconnected gmail"
}
```

---

## Integration Guide for AI Agents

### Step 1: Fetch Available Tools

```python
import requests

API_BASE = "http://localhost:8001"
API_KEY = "your_agent_api_key"
USER_ID = "110610502660943882433"

# Get tools with full schemas from Composio
response = requests.get(
    f"{API_BASE}/api/tools",
    params={"user_id": USER_ID},
    headers={"X-API-Key": API_KEY}
)
tools = response.json()["tools"]
```

### Step 2: Convert to OpenAI Function Format

```python
openai_tools = []
for tool in tools:
    openai_tools.append({
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]
        }
    })
```

### Step 3: Use with OpenAI

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You help users manage email and Slack."},
        {"role": "user", "content": "Send an email to bob@example.com saying hello"}
    ],
    tools=openai_tools,
    tool_choice="auto"
)

# If GPT-4 wants to call a function
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    # Execute via MCP Service
    result = requests.post(
        f"{API_BASE}/api/tools/execute",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "user_id": USER_ID,
            "action": function_name,
            "params": arguments
        }
    )
    print(result.json())
```

### Complete Integration Example

```python
class MCPClient:
    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base
        self.headers = {"X-API-Key": api_key}

    def get_tools(self, user_id: str) -> list:
        """Fetch available tools for a user."""
        resp = requests.get(
            f"{self.api_base}/api/tools",
            params={"user_id": user_id},
            headers=self.headers
        )
        return resp.json()["tools"]

    def execute(self, user_id: str, action: str, params: dict) -> dict:
        """Execute a tool action."""
        resp = requests.post(
            f"{self.api_base}/api/tools/execute",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"user_id": user_id, "action": action, "params": params}
        )
        return resp.json()

# Usage
client = MCPClient("http://localhost:8001", "your_api_key")
tools = client.get_tools("110610502660943882433")
result = client.execute(
    "110610502660943882433",
    "GMAIL_SEND_EMAIL",
    {"recipient_email": "bob@example.com", "subject": "Hi", "body": "Hello!"}
)
```

---

## Error Codes

| HTTP Code | Meaning |
|-----------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (invalid API key or token) |
| 404 | Not found (unknown provider or action) |
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
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `JWT_SECRET` | Secret for JWT signing | Yes |

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
