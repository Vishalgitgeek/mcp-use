"""MCP server configuration management."""
from typing import Dict
import os
from google.oauth2.credentials import Credentials
from config import FILESYSTEM_BASE_PATH
import json

# __________________________________________________________


def build_mcp_config(credentials: Credentials, include_gdrive: bool = True) -> Dict:
    """
    Build MCP server configuration by loading mcp_multi.json and injecting credentials.
    
    Args:
        credentials: Google OAuth credentials
        include_gdrive: Whether to include Google Drive MCP server
        
    Returns:
        MCP server configuration dictionary
    """
    # 1. Locate and Load the JSON Configuration
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'mcp_multi.json')
    
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        return {"mcpServers": {}}

    mcp_servers = config.get("mcpServers", {})

    # 2. Configure Filesystem (Inject Base Path)
    if "filesystem" in mcp_servers:
        fs_args = mcp_servers["filesystem"]["args"]
        # Replace the placeholder {FILESYSTEM_BASE_PATH} with the actual variable
        mcp_servers["filesystem"]["args"] = [
            arg.replace("{FILESYSTEM_BASE_PATH}", FILESYSTEM_BASE_PATH) 
            for arg in fs_args
        ]

    # 3. Configure Google Drive (Inject Token or Remove if disabled)
    if include_gdrive and "gdrive" in mcp_servers:
        try:
            gdrive_args = mcp_servers["gdrive"]["args"]
            # Replace the placeholder {ACCESS_TOKEN} with the actual token
            mcp_servers["gdrive"]["args"] = [
                arg.replace("{ACCESS_TOKEN}", credentials.token) 
                for arg in gdrive_args
            ]
        except Exception:
            # If token access fails, remove gdrive to prevent crash
            print("Warning: Failed to inject credentials for GDrive. Disabling.")
            del mcp_servers["gdrive"]
    else:
        # If include_gdrive is False, ensure we remove it from the config
        if "gdrive" in mcp_servers:
            del mcp_servers["gdrive"]

    return config


# __________________________________________________________

# def build_mcp_config(credentials: Credentials, include_gdrive: bool = True) -> Dict:
    """
    Build MCP server configuration with Google Drive credentials.
    
    Args:
        credentials: Google OAuth credentials
        include_gdrive: Whether to include Google Drive MCP server (may not work)
        
    Returns:
        MCP server configuration dictionary
    """
    config = {
        "mcpServers": {
            "filesystem": {
                "command": "cmd",
                "args": [
                    "/c", "npx", "-y", "@modelcontextprotocol/server-filesystem",
                    FILESYSTEM_BASE_PATH
                ]
            }
        }
    }
    
    # Note: Google Drive MCP server is deprecated and may not work properly
    # The server requires authentication setup that's not straightforward
    # For now, we'll skip it and use filesystem only
    # TODO: Implement custom Google Drive MCP server or find working alternative
    if include_gdrive:
        # Try with access token as argument (may not work)
        try:
            config["mcpServers"]["gdrive"] = {
                "command": "cmd",
                "args": [
                    "/c", "npx", "-y", "@modelcontextprotocol/server-gdrive",
                    "--access-token", credentials.token
                ]
            }
        except Exception:
            # If it fails, we'll just use filesystem
            pass
    
    return config

