# MCP Integration Service - API Reference v2.0

## Overview

The MCP Integration Service provides a REST API for managing OAuth integrations and exposing tools to AI agents. All endpoints (except OAuth callbacks and health check) require API key authentication.

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

All endpoints (except `/api/integrations/callback` and `/api/tools/health`) require the `X-API-Key` header:

```
X-API-Key: your_agent_api_key
```

Set `AGENT_API_KEY` in your `.env` file. This key is used by your backend/agents to authenticate.

---

## Supported Integrations

| Category | Provider | Description |
|----------|----------|-------------|
| **Email** | `gmail` | Send, read, and manage Gmail emails |
| **Communication** | `slack` | Send messages and interact with Slack workspaces |
| **Communication** | `whatsapp` | Send messages via WhatsApp Business API |
| **Productivity** | `googledocs` | Create, edit, and manage Google Docs |
| **Productivity** | `googlesheets` | Create, edit, and manage Google Sheets |
| **Storage** | `googledrive` | Access and manage files in Google Drive |
| **Data** | `googlebigquery` | Query and analyze data in BigQuery |
| **Video** | `googlemeet` | Schedule and manage Google Meet meetings |
| **Marketing** | `googleads` | Manage Google Ads campaigns |
| **Location** | `googlemaps` | Access Google Maps services |
| **Video** | `zoom` | Create and manage Zoom meetings |
| **Media** | `youtube` | Upload and manage YouTube videos |
| **Database** | `supabase` | Interact with Supabase database |
| **Social** | `linkedin` | Post content and manage LinkedIn |
| **Social** | `facebook` | Post content and manage Facebook pages |
| **Payment** | `stripe` | Process payments and subscriptions |

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
  "service": "mcp-integration-service"
}
```

---

## Integration Endpoints

### List Available Integrations

```http
GET /api/integrations?detailed={boolean}
```

**Headers:**
- `X-API-Key` (required): Your API key

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| detailed | boolean | true | If true, returns full details. If false, returns simple list. |

**Response (detailed=true, default):**
```json
{
  "integrations": [
    {
      "provider": "gmail",
      "name": "Gmail",
      "description": "Send, read, and manage emails via Google Gmail",
      "category": "Email"
    },
    {
      "provider": "slack",
      "name": "Slack",
      "description": "Send messages and interact with Slack workspaces",
      "category": "Communication"
    }
  ],
  "total": 16
}
```

**Response (detailed=false):**
```json
["gmail", "slack", "whatsapp", "googledocs", "googlesheets", "googledrive", "googlebigquery", "googlemeet", "googleads", "googlemaps", "zoom", "youtube", "supabase", "linkedin", "facebook", "stripe"]
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
    },
    {
      "provider": "slack",
      "status": "active",
      "connected_email": null,
      "connected_at": "2024-01-16T14:00:00Z"
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
| provider | string | Yes | Integration provider (see supported list) |
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
- `provider`: Integration provider (e.g., `gmail`, `slack`)

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

If not connected:
```json
{
  "provider": "gmail",
  "status": "not_connected"
}
```

---

### OAuth Callback (Internal)

```http
GET /api/integrations/callback
```

This endpoint is called by Composio after user completes OAuth. **No API key required.**

**Query Parameters (from Composio):**
| Name | Type | Description |
|------|------|-------------|
| status | string | OAuth status (`success` or error) |
| appName | string | Provider name |
| connectedAccountId | string | Composio connection ID |
| session_id | string | Session ID for redirect URL lookup |
| error | string | Error code (if failed) |
| error_description | string | Error message (if failed) |

**Behavior:**
- Uses `session_id` to look up the user's desired redirect URL from MongoDB
- Appends OAuth result parameters to the redirect URL
- Redirects (307) to: `{redirect_url}?status=success&appName=gmail` on success
- Redirects (307) to: `{redirect_url}?error={error}&message={description}` on failure

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

### List Provider Actions

```http
GET /api/tools/actions/{provider}?include_schema={boolean}
```

**Headers:**
- `X-API-Key` (required): Your API key

**Path Parameters:**
- `provider`: Provider name (e.g., `gmail`, `slack`, `zoom`)

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| include_schema | boolean | true | Include request/response schemas from Composio |

**Example:**
```bash
curl -X GET "https://mcp.openanalyst.com/api/tools/actions/gmail?include_schema=true" \
  -H "X-API-Key: your_api_key"
```

**Response (with schema):**
```json
{
  "provider": "gmail",
  "actions": [
    {
      "name": "GMAIL_SEND_EMAIL",
      "description": "Send an email",
      "request_schema": {
        "type": "object",
        "properties": {
          "recipient_email": {"type": "string"},
          "subject": {"type": "string"},
          "body": {"type": "string"}
        },
        "required": ["recipient_email", "subject", "body"]
      },
      "response_schema": {
        "type": "object",
        "properties": {
          "messageId": {"type": "string"},
          "threadId": {"type": "string"}
        }
      }
    }
  ],
  "schema_included": true,
  "total_actions": 12
}
```

**Response (without schema):**
```json
{
  "provider": "gmail",
  "actions": [
    {"name": "GMAIL_SEND_EMAIL", "description": "Send an email"},
    {"name": "GMAIL_FETCH_EMAILS", "description": "Fetch/search emails with optional query filter"}
  ],
  "schema_included": false,
  "total_actions": 12
}
```

---

### Get Action Schema

```http
GET /api/tools/schema/{action}
```

**Headers:**
- `X-API-Key` (required): Your API key

**Path Parameters:**
- `action`: Action name (e.g., `GMAIL_SEND_EMAIL`)

**Example:**
```bash
curl -X GET "https://mcp.openanalyst.com/api/tools/schema/GMAIL_SEND_EMAIL" \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "action": "GMAIL_SEND_EMAIL",
  "description": "Send an email via Gmail",
  "parameters": {
    "type": "object",
    "properties": {
      "recipient_email": {
        "type": "string",
        "description": "Email address of the recipient"
      },
      "subject": {
        "type": "string",
        "description": "Subject line of the email"
      },
      "body": {
        "type": "string",
        "description": "Body content of the email"
      }
    },
    "required": ["recipient_email", "subject", "body"]
  }
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

## Available Actions by Provider

### Gmail Actions

| Action | Description |
|--------|-------------|
| `GMAIL_SEND_EMAIL` | Send an email |
| `GMAIL_FETCH_EMAILS` | Fetch/search emails with optional query filter |
| `GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID` | Get a specific email by message ID |
| `GMAIL_FETCH_MESSAGE_BY_THREAD_ID` | Get all messages in a thread |
| `GMAIL_CREATE_EMAIL_DRAFT` | Create an email draft |
| `GMAIL_ADD_LABEL_TO_EMAIL` | Add or remove labels from an email |
| `GMAIL_LIST_LABELS` | List all Gmail labels |
| `GMAIL_DELETE_MESSAGE` | Permanently delete an email |
| `GMAIL_MARK_EMAIL_AS_READ` | Mark an email as read |
| `GMAIL_MARK_EMAIL_AS_UNREAD` | Mark an email as unread |
| `GMAIL_TRASH_MESSAGE` | Move message to trash |
| `GMAIL_GET_PROFILE` | Get Gmail user profile information |

### Slack Actions

| Action | Description |
|--------|-------------|
| `SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL` | Send a message to a channel |
| `SLACK_LIST_ALL_SLACK_TEAM_CHANNELS_WITH_PAGINATION` | List available channels |
| `SLACK_FETCHES_CONVERSATION_HISTORY` | Get channel message history |
| `SLACK_SEARCH_MESSAGES_IN_SLACK` | Search for messages |
| `SLACK_UPDATE_A_MESSAGE` | Update an existing message |
| `SLACK_DELETE_A_MESSAGE` | Delete a message |
| `SLACK_GET_CHANNEL_INFO` | Get information about a channel |
| `SLACK_CREATE_CHANNEL` | Create a new channel |

### WhatsApp Actions

| Action | Description |
|--------|-------------|
| `WHATSAPP_SEND_MESSAGE` | Send a WhatsApp message |
| `WHATSAPP_SEND_TEMPLATE_MESSAGE` | Send a template message |
| `WHATSAPP_SEND_MEDIA` | Send media (image, video, document) |
| `WHATSAPP_GET_MESSAGES` | Get incoming messages |
| `WHATSAPP_MARK_AS_READ` | Mark message as read |

### Zoom Actions

| Action | Description |
|--------|-------------|
| `ZOOM_CREATE_MEETING` | Create a new Zoom meeting |
| `ZOOM_LIST_MEETINGS` | List all scheduled meetings |
| `ZOOM_GET_MEETING` | Get meeting details |
| `ZOOM_UPDATE_MEETING` | Update meeting details |
| `ZOOM_DELETE_MEETING` | Delete a meeting |
| `ZOOM_START_MEETING` | Start a scheduled meeting |
| `ZOOM_END_MEETING` | End an active meeting |
| `ZOOM_LIST_RECORDINGS` | List meeting recordings |

### Google Docs Actions

| Action | Description |
|--------|-------------|
| `GOOGLEDOCS_CREATE_DOCUMENT` | Create a new Google Doc |
| `GOOGLEDOCS_GET_DOCUMENT` | Get document content |
| `GOOGLEDOCS_UPDATE_DOCUMENT` | Update document content |
| `GOOGLEDOCS_DELETE_DOCUMENT` | Delete a document |
| `GOOGLEDOCS_INSERT_TEXT` | Insert text at a specific location |
| `GOOGLEDOCS_REPLACE_TEXT` | Replace text in document |
| `GOOGLEDOCS_FORMAT_TEXT` | Format text (bold, italic, etc.) |

### Google Sheets Actions

| Action | Description |
|--------|-------------|
| `GOOGLESHEETS_CREATE_SPREADSHEET` | Create a new spreadsheet |
| `GOOGLESHEETS_GET_SPREADSHEET` | Get spreadsheet data |
| `GOOGLESHEETS_UPDATE_CELL` | Update cell value |
| `GOOGLESHEETS_UPDATE_RANGE` | Update a range of cells |
| `GOOGLESHEETS_APPEND_ROW` | Append a new row |
| `GOOGLESHEETS_DELETE_ROW` | Delete a row |
| `GOOGLESHEETS_CREATE_SHEET` | Create a new sheet in spreadsheet |
| `GOOGLESHEETS_GET_VALUES` | Get values from a range |

### Google Drive Actions

| Action | Description |
|--------|-------------|
| `GOOGLEDRIVE_LIST_FILES` | List files in Google Drive |
| `GOOGLEDRIVE_UPLOAD_FILE` | Upload a file to Drive |
| `GOOGLEDRIVE_DOWNLOAD_FILE` | Download a file from Drive |
| `GOOGLEDRIVE_DELETE_FILE` | Delete a file |
| `GOOGLEDRIVE_CREATE_FOLDER` | Create a new folder |
| `GOOGLEDRIVE_MOVE_FILE` | Move file to another folder |
| `GOOGLEDRIVE_SHARE_FILE` | Share a file with others |
| `GOOGLEDRIVE_SEARCH_FILES` | Search for files |
| `GOOGLEDRIVE_GET_FILE_METADATA` | Get file metadata |

### YouTube Actions

| Action | Description |
|--------|-------------|
| `YOUTUBE_UPLOAD_VIDEO` | Upload a video to YouTube |
| `YOUTUBE_LIST_VIDEOS` | List channel videos |
| `YOUTUBE_GET_VIDEO` | Get video details |
| `YOUTUBE_UPDATE_VIDEO` | Update video metadata |
| `YOUTUBE_DELETE_VIDEO` | Delete a video |
| `YOUTUBE_SEARCH_VIDEOS` | Search for videos |
| `YOUTUBE_LIST_PLAYLISTS` | List channel playlists |
| `YOUTUBE_CREATE_PLAYLIST` | Create a new playlist |
| `YOUTUBE_ADD_VIDEO_TO_PLAYLIST` | Add video to playlist |

### Google Meet Actions

| Action | Description |
|--------|-------------|
| `GOOGLEMEET_CREATE_MEETING` | Create a Google Meet meeting |
| `GOOGLEMEET_SCHEDULE_MEETING` | Schedule a meeting with calendar event |
| `GOOGLEMEET_GET_MEETING` | Get meeting details |
| `GOOGLEMEET_UPDATE_MEETING` | Update meeting details |
| `GOOGLEMEET_DELETE_MEETING` | Delete a meeting |

### Google Ads Actions

| Action | Description |
|--------|-------------|
| `GOOGLEADS_CREATE_CAMPAIGN` | Create an ad campaign |
| `GOOGLEADS_LIST_CAMPAIGNS` | List all campaigns |
| `GOOGLEADS_GET_CAMPAIGN` | Get campaign details |
| `GOOGLEADS_UPDATE_CAMPAIGN` | Update campaign settings |
| `GOOGLEADS_PAUSE_CAMPAIGN` | Pause a campaign |
| `GOOGLEADS_GET_CAMPAIGN_STATS` | Get campaign statistics |
| `GOOGLEADS_CREATE_AD_GROUP` | Create an ad group |
| `GOOGLEADS_GET_KEYWORDS` | Get campaign keywords |

### Google Maps Actions

| Action | Description |
|--------|-------------|
| `GOOGLEMAPS_GEOCODE` | Convert address to coordinates |
| `GOOGLEMAPS_REVERSE_GEOCODE` | Convert coordinates to address |
| `GOOGLEMAPS_GET_DIRECTIONS` | Get directions between locations |
| `GOOGLEMAPS_DISTANCE_MATRIX` | Calculate distances and travel times |
| `GOOGLEMAPS_PLACES_SEARCH` | Search for places |
| `GOOGLEMAPS_PLACE_DETAILS` | Get place details |
| `GOOGLEMAPS_ELEVATION` | Get elevation data |

### Supabase Actions

| Action | Description |
|--------|-------------|
| `SUPABASE_INSERT_ROW` | Insert a row into table |
| `SUPABASE_SELECT_ROWS` | Query rows from table |
| `SUPABASE_UPDATE_ROW` | Update a row in table |
| `SUPABASE_DELETE_ROW` | Delete a row from table |
| `SUPABASE_EXECUTE_RPC` | Execute stored procedure |
| `SUPABASE_CREATE_USER` | Create authentication user |
| `SUPABASE_UPLOAD_FILE` | Upload file to storage |
| `SUPABASE_DOWNLOAD_FILE` | Download file from storage |

### LinkedIn Actions

| Action | Description |
|--------|-------------|
| `LINKEDIN_CREATE_POST` | Create a LinkedIn post |
| `LINKEDIN_SHARE_ARTICLE` | Share an article |
| `LINKEDIN_GET_PROFILE` | Get profile information |
| `LINKEDIN_UPDATE_PROFILE` | Update profile details |
| `LINKEDIN_SEND_MESSAGE` | Send a message to connection |
| `LINKEDIN_GET_CONNECTIONS` | Get list of connections |
| `LINKEDIN_CREATE_COMPANY_POST` | Post on company page |

### Facebook Actions

| Action | Description |
|--------|-------------|
| `FACEBOOK_CREATE_POST` | Create a post on page |
| `FACEBOOK_UPLOAD_PHOTO` | Upload a photo |
| `FACEBOOK_UPLOAD_VIDEO` | Upload a video |
| `FACEBOOK_GET_PAGE_INSIGHTS` | Get page analytics |
| `FACEBOOK_GET_POSTS` | Get page posts |
| `FACEBOOK_DELETE_POST` | Delete a post |
| `FACEBOOK_SEND_MESSAGE` | Send message via Messenger |
| `FACEBOOK_CREATE_AD` | Create a Facebook ad |

### Stripe Actions

| Action | Description |
|--------|-------------|
| `STRIPE_CREATE_CUSTOMER` | Create a new customer |
| `STRIPE_GET_CUSTOMER` | Get customer details |
| `STRIPE_CREATE_PAYMENT_INTENT` | Create payment intent |
| `STRIPE_CAPTURE_PAYMENT` | Capture a payment |
| `STRIPE_REFUND_PAYMENT` | Refund a payment |
| `STRIPE_CREATE_SUBSCRIPTION` | Create a subscription |
| `STRIPE_CANCEL_SUBSCRIPTION` | Cancel a subscription |
| `STRIPE_LIST_INVOICES` | List customer invoices |
| `STRIPE_CREATE_PRODUCT` | Create a product |
| `STRIPE_GET_BALANCE` | Get account balance |

---

## Integration Flow

### 1. Connect a User's Account

```
Your Backend                    MCP Service                    Composio
    |                               |                               |
    |-- POST /connect ------------->|                               |
    |   {user_id, provider,         |-- Store session_id ---------->|
    |    redirect_url}              |   in MongoDB                  |
    |                               |                               |
    |<-- {auth_url} ----------------|                               |
    |                               |                               |
    |-- Redirect user to auth_url --------------------------------->|
    |                               |                               |
    |                               |<-- Callback with session_id --|
    |                               |                               |
    |                               |-- Look up redirect_url ------>|
    |                               |   from session_id             |
    |                               |                               |
    |<-- Redirect to your app ------|                               |
    |   ?status=success&appName=... |                               |
```

### 2. Discover Available Actions

```
Your AI Agent                   MCP Service                    Composio API
    |                               |                               |
    |-- GET /actions/gmail -------->|                               |
    |   ?include_schema=true        |-- Fetch schemas ------------->|
    |                               |                               |
    |<-- {actions with schemas} ----|<-- Schema data ---------------|
```

### 3. Execute Tools

```
Your AI Agent                   MCP Service                    Gmail/Slack/etc
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

class MCPClient:
    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base
        self.headers = {"X-API-Key": api_key}

    def list_integrations(self):
        """List all available integrations."""
        resp = requests.get(
            f"{self.api_base}/api/integrations",
            headers=self.headers
        )
        return resp.json()

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

    def get_provider_actions(self, provider: str, include_schema: bool = True):
        """Get available actions for a provider with schemas."""
        resp = requests.get(
            f"{self.api_base}/api/tools/actions/{provider}",
            params={"include_schema": include_schema},
            headers=self.headers
        )
        return resp.json()

    def get_action_schema(self, action: str, user_id: str):
        """Get detailed schema for a specific action."""
        resp = requests.get(
            f"{self.api_base}/api/tools/schema/{action}",
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

# 1. List available integrations
integrations = client.list_integrations()
print(f"Available: {integrations}")

# 2. Connect Gmail for a user (redirect user to auth_url)
result = client.connect_integration("user_123", "gmail", "https://your-app.com/done")
print(f"Redirect user to: {result['auth_url']}")

# 3. After OAuth, check connected integrations
connected = client.get_connected("user_123")
print(f"Connected: {connected}")

# 4. Get available actions for Gmail (with schemas)
actions = client.get_provider_actions("gmail", include_schema=True)
print(f"Gmail actions: {actions['total_actions']}")

# 5. Get available tools for user
tools = client.get_tools("user_123")
print(f"Available tools: {[t['name'] for t in tools]}")

# 6. Execute a tool
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
| 307 | Redirect (OAuth callback) |
| 400 | Bad request (invalid parameters, unsupported provider) |
| 401 | Unauthorized (invalid or missing API key) |
| 404 | Not found (unknown provider, action, or resource) |
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

- API docs (Swagger): `http://localhost:8001/docs`
- API docs (ReDoc): `http://localhost:8001/redoc`
- Health check: `http://localhost:8001/api/tools/health`

---

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_tools_api.py -v
```
