# Actions Configuration Management

This directory contains the actions configuration system for managing provider actions in your MCP Integration Service.

## 📁 File

### `actions_config.py`
**Centralized configuration file** where you define all available actions for each Composio integration provider.

- Contains `PROVIDER_ACTIONS` dictionary with actions for each provider
- Helper functions to query and search actions
- Supports all enabled providers from `tools_config.py`

## 🚀 How to Use

### 1. **View Actions for a Provider**

```python
from mcp_service.actions_config import get_provider_actions

# Get Gmail actions
gmail_actions = get_provider_actions("gmail")
# Returns: [{"name": "GMAIL_SEND_EMAIL", "description": "..."}, ...]
```

### 2. **Add Actions for a New Provider**

Edit `mcp_service/actions_config.py`:

```python
PROVIDER_ACTIONS = {
    "gmail": [...],
    "slack": [...],
    
    # Add your new provider
    "notion": [
        {"name": "NOTION_CREATE_PAGE", "description": "Create a new page"},
        {"name": "NOTION_UPDATE_PAGE", "description": "Update a page"},
        {"name": "NOTION_DELETE_PAGE", "description": "Delete a page"},
        {"name": "NOTION_SEARCH", "description": "Search in workspace"},
    ],
}
```

**No restart needed!** The API will pick up changes immediately since actions are loaded on each request.

### 3. **Check Available Providers**

```python
from mcp_service.actions_config import get_all_providers

providers = get_all_providers()
# Returns: ["gmail", "slack", "docs", "sheet", "drive", "github", "bitbucket", "youtube"]
```

### 4. **Search for Actions**

```python
from mcp_service.actions_config import search_actions

# Search across all providers
results = search_actions("email")
# Returns: [{"provider": "gmail", "name": "GMAIL_SEND_EMAIL", ...}, ...]

# Search within a specific provider
results = search_actions("create", provider="github")
# Returns only GitHub actions containing "create"
```

## 📊 Current Actions Defined

### Email & Communication
- **Gmail**: 12 actions (send, fetch, draft, labels, etc.)
- **Slack**: 8 actions (message, channels, search, etc.)

### Google Services
- **Google Docs**: 7 actions (create, update, format, etc.)
- **Google Sheets**: 8 actions (create, update cells, append rows, etc.)
- **Google Drive**: 9 actions (list, upload, download, share, etc.)

### Development & Version Control
- **GitHub**: 14 actions (issues, PRs, repos, files, commits)
- **Bitbucket**: 8 actions (repos, PRs, issues, files)

### Media
- **YouTube**: 9 actions (upload, playlists, metadata, etc.)

## 🎯 API Endpoint

Actions are exposed via the API endpoint:

```http
GET /api/tools/actions/{provider}
X-API-Key: your_api_key
```

**Example:**
```bash
curl http://localhost:8001/api/tools/actions/gmail \
  -H "X-API-Key: your_key"
```

**Response:**
```json
{
  "provider": "gmail",
  "actions": [
    {
      "name": "GMAIL_SEND_EMAIL",
      "description": "Send an email"
    },
    ...
  ]
}
```

## 📝 Best Practices

### Finding Composio Action Names

To get accurate action names from Composio:

```python
from composio import Composio

c = Composio(api_key="your_key")

# Get all actions for Gmail
tools = c.tools.get(toolkits=["GMAIL"])
for tool in tools:
    print(f"- {tool.name}: {tool.description}")
```

### Organizing Actions

Group actions logically in the configuration:

```python
"gmail": [
    # Sending & receiving
    {"name": "GMAIL_SEND_EMAIL", "description": "..."},
    {"name": "GMAIL_FETCH_EMAILS", "description": "..."},
    
    # Labels & organization  
    {"name": "GMAIL_ADD_LABEL_TO_EMAIL", "description": "..."},
    {"name": "GMAIL_LIST_LABELS", "description": "..."},
    
    # Drafts
    {"name": "GMAIL_CREATE_EMAIL_DRAFT", "description": "..."},
],
```

### Keep Descriptions Clear

Write clear, concise descriptions for AI agents:

```python
# ✓ Good
{"name": "GMAIL_SEND_EMAIL", "description": "Send an email"}

# ✗ Less helpful
{"name": "GMAIL_SEND_EMAIL", "description": "Sends an email message via Gmail API"}
```

## 🔧 Helper Functions Reference

### `get_provider_actions(provider: str) -> list`
Get all actions for a provider.

### `get_all_providers() -> list`
Get list of all providers with actions defined.

### `is_provider_supported(provider: str) -> bool`
Check if a provider has actions.

### `get_action_count(provider: str) -> int`
Get number of actions for a provider.

### `search_actions(query: str, provider: str = None) -> list`
Search actions by name or description.

## 🆕 Adding a New Provider

**Complete Workflow:**

1. **Add tool to `tools_config.py`:**
   ```python
   ENABLED_TOOLS = {
       "notion": "ac_YOUR_NOTION_CONFIG_ID",
   }
   ```

2. **Define actions in `actions_config.py`:**
   ```python
   PROVIDER_ACTIONS = {
       "notion": [
           {"name": "NOTION_CREATE_PAGE", "description": "Create page"},
           {"name": "NOTION_UPDATE_PAGE", "description": "Update page"},
       ]
   }
   ```

3. **Sync tools to database:**
   ```bash
   python -m mcp_service.scripts.sync_tools_to_db
   ```

4. **Test the endpoint:**
   ```bash
   curl http://localhost:8001/api/tools/actions/notion \
     -H "X-API-Key: your_key"
   ```

## ⚡ No Restart Required

Unlike `tools_config.py` which requires a service restart, **actions_config.py changes are picked up immediately** because:

- Actions are loaded on each API request
- No caching of action definitions
- Hot-reload friendly

## 📊 Example: Complete Provider Configuration

```python
"trello": [
    # Boards
    {"name": "TRELLO_CREATE_BOARD", "description": "Create a new board"},
    {"name": "TRELLO_LIST_BOARDS", "description": "List all boards"},
    {"name": "TRELLO_GET_BOARD", "description": "Get board details"},
    
    # Lists
    {"name": "TRELLO_CREATE_LIST", "description": "Create a list on board"},
    {"name": "TRELLO_GET_LISTS", "description": "Get all lists on board"},
    
    # Cards
    {"name": "TRELLO_CREATE_CARD", "description": "Create a card"},
    {"name": "TRELLO_UPDATE_CARD", "description": "Update a card"},
    {"name": "TRELLO_MOVE_CARD", "description": "Move card to another list"},
    {"name": "TRELLO_DELETE_CARD", "description": "Delete a card"},
    
    # Members
    {"name": "TRELLO_ADD_MEMBER", "description": "Add member to board"},
    {"name": "TRELLO_REMOVE_MEMBER", "description": "Remove member from board"},
]
```

## 🎉 Benefits

- ✅ **Centralized** - All actions in one file
- ✅ **Hot-reload** - No service restart needed
- ✅ **Version Control** - Track changes in Git
- ✅ **Searchable** - Built-in search functionality
- ✅ **Organized** - Group by provider and category
- ✅ **Flexible** - Easy to add/remove actions
- ✅ **Type-safe** - Helper functions with type hints
