"""MCP server configuration management."""
import json
import os
from typing import Dict
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials

# Load environment variables from .env file
load_dotenv()

def expand_env_vars(obj):
    """
    Recursively replace ${VAR} with values from .env.
    """
    if isinstance(obj, dict):
        return {k: expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_env_vars(i) for i in obj]
    elif isinstance(obj, str):
        # Only expands variables that exist in .env
        return os.path.expandvars(obj)
    else:
        return obj

def build_mcp_config(credentials: Credentials, include_gdrive: bool = True) -> Dict:
    """
    Build MCP configuration using .env for static paths and arguments 
    for dynamic credentials.
    """
    
    # 1. Load the JSON template
    config_path = os.path.join(os.path.dirname(__file__), 'mcp_multi.json')
    try:
        with open(config_path, 'r') as f:
            raw_config = json.load(f)
    except FileNotFoundError:
        print("Error: mcp_multi.json not found.")
        return {"mcpServers": {}}

    # 2. Fill in static .env values (Paths, IDs, Secrets)
    config = expand_env_vars(raw_config)
    
    mcp_servers = config.get("mcpServers", {})

    # 3. Handle Google Drive Logic
    if include_gdrive and "gdrive" in mcp_servers:
        try:
            # We need to manually inject the dynamic token from the 'credentials' object
            # because this doesn't exist in the .env file.
            gdrive_args = mcp_servers["gdrive"]["args"]
            
            mcp_servers["gdrive"]["args"] = [
                arg.replace("${DYNAMIC_ACCESS_TOKEN}", credentials.token) 
                for arg in gdrive_args
            ]
        except Exception as e:
            print(f"Warning: Failed to inject GDrive token: {e}")
            del mcp_servers["gdrive"]
    else:
        # If include_gdrive is False, strictly remove it
        if "gdrive" in mcp_servers:
            del mcp_servers["gdrive"]

    return config

