# MCP Server Issues

## Current Status

The Google Drive MCP server (`@modelcontextprotocol/server-gdrive`) is **deprecated** and has configuration issues:

1. It doesn't accept `--access-token` as a command line argument
2. It requires running an `auth` command first to set up credentials
3. The authentication flow is not compatible with our OAuth setup

## Current Solution

For now, the system is configured to use **only the filesystem MCP server**. This means:

- ✅ You can read/write local files
- ❌ Google Drive operations are not available through MCP

## Future Options

### Option 1: Build Custom Google Drive MCP Server
Create a custom MCP server that:
- Accepts OAuth tokens directly
- Implements Google Drive API operations
- Works with our existing authentication flow

### Option 2: Use Google Drive API Directly
Instead of MCP, use the Google Drive API directly in the agent service:
- Use `google-api-python-client` to interact with Drive
- Pass Drive operations as tools to the agent
- More control but less standardized

### Option 3: Find Alternative MCP Server
Look for community-maintained Google Drive MCP servers that work better.

## Temporary Workaround

If you need Google Drive functionality now, you can:

1. Use the Google Drive API directly in Python
2. Create custom tools/functions for the agent
3. Implement Drive operations as part of the agent service

The filesystem MCP server works fine for local file operations.

