"""Configuration for MCP Integration Service."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (override=True ensures .env takes precedence)
load_dotenv(override=True)

# Base paths
BASE_DIR = Path(__file__).parent.parent
SERVICE_DIR = Path(__file__).parent

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "mcp_integrations")

# Composio Configuration
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY", "")

# Server Configuration
SERVER_HOST = os.getenv("MCP_SERVICE_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("MCP_SERVICE_PORT", "8001"))

# API Key for agent authentication
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")

# Supported integrations (initial set)
SUPPORTED_INTEGRATIONS = ["gmail", "slack"]

# OAuth Redirect Base URL
OAUTH_REDIRECT_BASE = os.getenv("OAUTH_REDIRECT_BASE", "http://localhost:8001")


def validate_config():
    """Validate required configuration is present."""
    errors = []

    if not COMPOSIO_API_KEY:
        errors.append("COMPOSIO_API_KEY is not set")

    if not AGENT_API_KEY:
        errors.append("AGENT_API_KEY is not set (needed for agent auth)")

    return errors
