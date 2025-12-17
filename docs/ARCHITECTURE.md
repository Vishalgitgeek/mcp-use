# MCP Integration Service - Architecture Guide

## System Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐              ┌─────────────────────────────────────┐  │
│  │   Web Browser   │              │         AI Agent (Your App)          │  │
│  │   (End Users)   │              │   - ChatGPT-like interface           │  │
│  │                 │              │   - Uses OpenAI function calling     │  │
│  └────────┬────────┘              └──────────────────┬──────────────────┘  │
│           │                                          │                      │
│           │ JWT Token                                │ API Key              │
│           │                                          │                      │
└───────────┼──────────────────────────────────────────┼──────────────────────┘
            │                                          │
            ▼                                          ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         MCP INTEGRATION SERVICE                             │
│                          (http://localhost:8001)                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                           FastAPI Application                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐ │   │
│  │  │  /auth/*       │  │ /api/          │  │ /api/tools/*           │ │   │
│  │  │                │  │ integrations/* │  │                        │ │   │
│  │  │ Google OAuth   │  │                │  │ GET  /api/tools        │ │   │
│  │  │ Login/Callback │  │ Connect        │  │ POST /api/tools/execute│ │   │
│  │  │ JWT Generation │  │ Disconnect     │  │ GET  /api/tools/actions│ │   │
│  │  │                │  │ List           │  │                        │ │   │
│  │  └────────────────┘  └────────────────┘  └────────────────────────┘ │   │
│  │         │                    │                      │                │   │
│  │         ▼                    ▼                      ▼                │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │                     Services Layer                            │   │   │
│  │  ├──────────────────────────────────────────────────────────────┤   │   │
│  │  │  IntegrationService          │       ComposioService         │   │   │
│  │  │  - Business logic            │       - SDK wrapper           │   │   │
│  │  │  - MongoDB operations        │       - OAuth initiation      │   │   │
│  │  │  - User management           │       - Tool execution        │   │   │
│  │  └──────────────────────────────┴───────────────────────────────┘   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└──────────────────────────────┬─────────────────────────┬────────────────────┘
                               │                         │
                               ▼                         ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────────┐
│              MongoDB                  │  │           Composio               │
├──────────────────────────────────────┤  ├──────────────────────────────────┤
│                                       │  │                                  │
│  Collections:                         │  │  Responsibilities:               │
│  ┌─────────────────────────────────┐ │  │  - OAuth flow management         │
│  │ users                            │ │  │  - Token storage & refresh       │
│  │ - google_id                      │ │  │  - Action execution              │
│  │ - email                          │ │  │  - Tool schema definitions       │
│  │ - name                           │ │  │                                  │
│  └─────────────────────────────────┘ │  │  Supported Apps:                  │
│  ┌─────────────────────────────────┐ │  │  - Gmail                         │
│  │ integrations                     │ │  │  - Slack                         │
│  │ - user_id                        │ │  │  - Google Docs                   │
│  │ - provider                       │ │  │  - GitHub                        │
│  │ - status                         │ │  │  - 100+ more...                  │
│  │ - composio_entity_id             │ │  │                                  │
│  └─────────────────────────────────┘ │  └──────────────────────────────────┘
│                                       │
└──────────────────────────────────────┘
```

## Data Flow

### Flow 1: User Connects Gmail

```
┌──────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────┐
│ User │     │    UI    │     │   API    │     │ Composio │     │ Google │
└──┬───┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └───┬────┘
   │              │                │                │               │
   │ Click Connect│                │                │               │
   │─────────────▶│                │                │               │
   │              │                │                │               │
   │              │ POST /connect  │                │               │
   │              │ {provider:gmail}                │               │
   │              │───────────────▶│                │               │
   │              │                │                │               │
   │              │                │ Get OAuth URL  │               │
   │              │                │───────────────▶│               │
   │              │                │                │               │
   │              │                │◀───────────────│               │
   │              │                │  auth_url      │               │
   │              │◀───────────────│                │               │
   │              │ {auth_url}     │                │               │
   │              │                │                │               │
   │◀─────────────│ Redirect       │                │               │
   │              │                │                │               │
   │ Login with Google────────────────────────────────────────────▶│
   │              │                │                │               │
   │◀────────────────────────────────────────────────Redirect──────│
   │              │                │                │               │
   │ ?connected=gmail              │                │               │
   │─────────────▶│                │                │               │
   │              │                │                │               │
   │              │ POST /complete │                │               │
   │              │───────────────▶│                │               │
   │              │                │ Update MongoDB │               │
   │              │                │ status=active  │               │
   │              │◀───────────────│                │               │
   │              │                │                │               │
   │◀─────────────│ Show Connected │                │               │
   │              │                │                │               │
```

### Flow 2: AI Agent Sends Email

```
┌───────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│  AI Agent │     │ MCP Service │     │ Composio │     │  Gmail   │
└─────┬─────┘     └──────┬──────┘     └────┬─────┘     └────┬─────┘
      │                  │                 │                │
      │ POST /execute    │                 │                │
      │ {action: GMAIL_  │                 │                │
      │  SEND_EMAIL,     │                 │                │
      │  params: {...}}  │                 │                │
      │─────────────────▶│                 │                │
      │                  │                 │                │
      │                  │ Verify API Key  │                │
      │                  │ Check MongoDB   │                │
      │                  │ (user has gmail)│                │
      │                  │                 │                │
      │                  │ tools.execute() │                │
      │                  │────────────────▶│                │
      │                  │                 │                │
      │                  │                 │ Use stored     │
      │                  │                 │ OAuth tokens   │
      │                  │                 │───────────────▶│
      │                  │                 │                │
      │                  │                 │◀───────────────│
      │                  │                 │  Email sent    │
      │                  │◀────────────────│                │
      │                  │  {success: true}│                │
      │◀─────────────────│                 │                │
      │  {success: true} │                 │                │
      │                  │                 │                │
```

## Key Concepts

### 1. Entity ID

Composio uses `entity_id` to identify users and their connected accounts.

```
user_id = "110610502660943882433"     # From Google OAuth
entity_id = "user_110610502660943882433"  # For Composio
```

The MCP Service automatically converts between these formats.

### 2. Integration Status

| Status | Meaning |
|--------|---------|
| `pending` | OAuth initiated but not completed |
| `active` | Successfully connected and usable |
| `expired` | OAuth tokens expired |
| `revoked` | User revoked access |
| `error` | Connection error |

### 3. Authentication Types

| Type | Used By | Header | Purpose |
|------|---------|--------|---------|
| JWT Token | Web UI | `Authorization: Bearer <token>` | User session |
| API Key | AI Agents | `X-API-Key: <key>` | Service auth |

## File Structure

```
mcp_service/
├── main.py                 # FastAPI app entry point
├── config.py               # Environment configuration
├── api/
│   ├── auth.py             # Authentication utilities
│   ├── google_auth.py      # Google OAuth routes
│   ├── integrations.py     # Integration management routes
│   └── tools.py            # Tool execution routes (for AI agents)
├── services/
│   ├── composio_service.py # Composio SDK wrapper
│   └── integration_service.py  # Business logic
├── models/
│   └── integration.py      # Pydantic models
└── db/
    └── mongodb.py          # Database connection

static/                     # Frontend UI
├── index.html
├── app.js
└── style.css

tests/
└── agent.py               # Test AI agent

docs/
├── API_REFERENCE.md       # API documentation
└── ARCHITECTURE.md        # This file
```

## Adding New Integrations

### Step 1: Add Auth Config

In `composio_service.py`:

```python
AUTH_CONFIG_MAP = {
    "gmail": "ac_24DkR_l4gcsg",
    "slack": "ac_EEgx5VnWdJz_",
    "github": "ac_XXXXX",  # Add new
}
```

### Step 2: Add to Supported List

In `config.py`:

```python
SUPPORTED_INTEGRATIONS = ["gmail", "slack", "github"]
```

### Step 3: Add Actions List

In `api/tools.py`:

```python
provider_actions = {
    "gmail": [...],
    "slack": [...],
    "github": [
        {"name": "GITHUB_CREATE_ISSUE", "description": "Create an issue"},
        {"name": "GITHUB_LIST_REPOS", "description": "List repositories"},
    ],
}
```

### Step 4: Update Agent (Optional)

In `tests/agent.py`, add the provider to the loop:

```python
for provider in ["gmail", "slack", "github"]:
```

## Security Considerations

1. **API Key Protection**: Never expose `AGENT_API_KEY` in client-side code
2. **JWT Expiration**: Tokens expire after 24 hours by default
3. **CORS**: Configure `allow_origins` in production
4. **HTTPS**: Use HTTPS in production
5. **MongoDB**: Use authentication in production

## Composio Integration

Composio handles:
- OAuth token storage (encrypted)
- Token refresh (automatic)
- Action execution (uses stored tokens)
- Rate limiting (per-app limits)

Your service handles:
- User management
- Integration status tracking
- API authentication
- Request routing

This separation means you never handle OAuth tokens directly - Composio manages them securely.
