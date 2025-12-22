# Tool Configuration Management

This directory contains the tool configuration system for managing which Composio integrations are available in your MCP Integration Service.

## 📁 Files

### `tools_config.py`
**Centralized configuration file** where you define which tools/integrations to expose.

- Contains `ENABLED_TOOLS` dictionary with `{app_name: auth_config_id}` mappings
- Optional metadata for each tool (category, description, etc.)
- Helper functions to query tool configuration

### `scripts/sync_tools_to_db.py`
**Synchronization script** that reads `tools_config.py` and updates MongoDB.

- Adds new tools to the database
- Updates existing tool configurations
- Disables tools removed from config
- Creates indexes for performance

## 🚀 How to Use

### 1. **Add a New Tool**

Edit `mcp_service/tools_config.py`:

```python
ENABLED_TOOLS = {
    "gmail": "ac_24DkR_l4gcsg",
    "slack": "ac_EEgx5VnWdJz_",
    "github": "ac_YOUR_GITHUB_CONFIG_ID",  # ← Add your new tool here
}
```

**How to get auth_config_id:**
1. Go to Composio Dashboard
2. Navigate to Auth Configs
3. Copy the config ID for your integration
4. Or use Python: `c.auth_configs.list()`

### 2. **Sync to Database**

Run the sync script:

```bash
python -m mcp_service.scripts.sync_tools_to_db
```

This will:
- ✓ Add new tools from config
- ✓ Update existing tools
- ✓ Disable tools not in config
- ✓ Create database indexes

### 3. **List Tools in Database**

To see what's currently in the database:

```bash
python -m mcp_service.scripts.sync_tools_to_db --list
```

### 4. **Restart Service** (if running)

After syncing, restart the MCP service:

```bash
# Stop the running service (Ctrl+C)
# Then restart:
python -m mcp_service.main
```

## 📊 Database Schema

Tools are stored in the `tools` collection with this structure:

```json
{
  "app_name": "gmail",
  "auth_config_id": "ac_24DkR_l4gcsg",
  "enabled": true,
  "category": "email",
  "description": "Send, read, and manage Gmail emails",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 🔧 Advanced Configuration

### Add Metadata

In `tools_config.py`, add metadata for better organization:

```python
TOOL_METADATA = {
    "github": {
        "category": "development",
        "description": "Interact with GitHub repositories",
        "enabled": True,
    }
}
```

### Disable a Tool

To temporarily disable a tool without removing it:

```python
TOOL_METADATA = {
    "slack": {
        "enabled": False,  # ← Disable it
    }
}
```

Then run sync script.

### Query by Category

```python
from mcp_service.tools_config import get_tools_by_category

email_tools = get_tools_by_category("email")
# Returns: {"gmail": "ac_24DkR_l4gcsg", ...}
```

## 📝 Example Workflow

### Adding GitHub Integration

1. **Get auth_config_id from Composio:**
   ```python
   from composio import Composio
   c = Composio(api_key="your_key")
   configs = c.auth_configs.list()
   # Find GitHub config ID
   ```

2. **Add to `tools_config.py`:**
   ```python
   ENABLED_TOOLS = {
       "gmail": "ac_24DkR_l4gcsg",
       "slack": "ac_EEgx5VnWdJz_",
       "github": "ac_AbCdEfGh123",  # Your GitHub config
   }
   
   TOOL_METADATA = {
       "github": {
           "category": "development",
           "description": "Create issues, manage repos, etc.",
           "enabled": True,
       }
   }
   ```

3. **Sync to database:**
   ```bash
   python -m mcp_service.scripts.sync_tools_to_db
   ```

4. **Verify it's added:**
   ```bash
   python -m mcp_service.scripts.sync_tools_to_db --list
   ```

## ⚠️ Important Notes

- **Always sync after editing** `tools_config.py`
- **Restart the service** after syncing to pick up changes
- **Keep auth_config_ids secure** - consider using environment variables for production
- **MongoDB must be running** before syncing

## 🎯 Benefits

- ✅ **Centralized Configuration**: All tools defined in one place
- ✅ **Version Control**: Track tool changes in Git
- ✅ **Easy Management**: Add/remove tools without touching code logic
- ✅ **Database Sync**: Automatically updates MongoDB
- ✅ **Flexible**: Can enable/disable tools without deletion
- ✅ **Organized**: Category-based grouping of tools
