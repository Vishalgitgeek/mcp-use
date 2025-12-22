"""
Tool Configuration - Define which Composio tools to expose in your service

This file defines which integrations/tools from Composio (300+ available) 
are enabled for your MCP Integration Service.

To add a new tool:
1. Get the auth_config_id from Composio dashboard or c.auth_configs.list()
2. Add it to ENABLED_TOOLS dictionary below
3. Run: python -m mcp_service.scripts.sync_tools_to_db
"""

# ============================================
# ENABLED TOOLS CONFIGURATION
# ============================================
# Format: "app_name": "auth_config_id"
# The auth_config_id is from your Composio account

ENABLED_TOOLS = {
    # Email & Communication
    "gmail": "ac_zU1jBJBYALeb",
    "slack": "ac_7v6eenDvYNbn",
    "whatsapp": "ac_CJJNCRZry5Uw",
    
    # Google Services
    "googledocs": "ac_q5dI1_V9PxNB",
    "googlesheets": "ac_QQmKApYUmXW_",
    "googledrive": "ac_2tyw32nZjQSC",
    "googlebigquery": "ac_MF8iPzJMYdQA",
    "googlemeet": "ac_nAHXEVU0UxX5",
    "googleads": "ac_doMQXNfhhEkb",
    "googlemaps": "ac_F-KJ911-9Qy_",
    
    # Video & Conferencing
    "zoom": "ac_2ygwF8hzKmyJ",
    "youtube": "ac_beaAbFcGVrX5",
    
    # Development & Database
    "supabase": "ac_JFhWNcKJRdCO",
    
    # Business & Marketing
    "linkedin": "ac_STVPw9h3slyp",
    "facebook": "ac_Q_6H1WLdn4qO",
    
    # Payment & Finance
    "stripe": "ac_EZVgKSjbaxHF",
    # "jira": "ac_YOUR_JIRA_CONFIG_ID",
    
    # Calendar
    # "google_calendar": "ac_YOUR_GCAL_CONFIG_ID",
    # "outlook_calendar": "ac_YOUR_OUTLOOK_CAL_CONFIG_ID",
    
    # Storage
    # "google_drive": "ac_YOUR_GDRIVE_CONFIG_ID",
    # "dropbox": "ac_YOUR_DROPBOX_CONFIG_ID",
    # "onedrive": "ac_YOUR_ONEDRIVE_CONFIG_ID",
    
    # CRM
    # "salesforce": "ac_YOUR_SALESFORCE_CONFIG_ID",
    # "hubspot": "ac_YOUR_HUBSPOT_CONFIG_ID",
    
    # Social Media
    # "twitter": "ac_YOUR_TWITTER_CONFIG_ID",
    # "linkedin": "ac_YOUR_LINKEDIN_CONFIG_ID",
    # "facebook": "ac_YOUR_FACEBOOK_CONFIG_ID",
}


# ============================================
# TOOL METADATA (Optional)
# ============================================
# Add descriptions and categories for better organization

TOOL_METADATA = {
    "gmail": {
        "category": "email",
        "description": "Send, read, and manage Gmail emails",
        "enabled": True,
    },
    "slack": {
        "category": "communication",
        "description": "Send messages and interact with Slack workspaces",
        "enabled": True,
    },
    "whatsapp": {
        "category": "communication",
        "description": "Send messages via WhatsApp Business API",
        "enabled": True,
    },
    "googledocs": {
        "category": "productivity",
        "description": "Create, edit, and manage Google Docs documents",
        "enabled": True,
    },
    "googlesheets": {
        "category": "productivity",
        "description": "Create, edit, and manage Google Sheets spreadsheets",
        "enabled": True,
    },
    "googledrive": {
        "category": "storage",
        "description": "Access and manage files in Google Drive",
        "enabled": True,
    },
    "googlebigquery": {
        "category": "data",
        "description": "Query and analyze data in Google BigQuery",
        "enabled": True,
    },
    "googlemeet": {
        "category": "video",
        "description": "Schedule and manage Google Meet video conferences",
        "enabled": True,
    },
    "googleads": {
        "category": "marketing",
        "description": "Manage Google Ads campaigns and analytics",
        "enabled": True,
    },
    "googlemaps": {
        "category": "location",
        "description": "Access Google Maps services and location data",
        "enabled": True,
    },
    "zoom": {
        "category": "video",
        "description": "Create and manage Zoom meetings",
        "enabled": True,
    },
    "youtube": {
        "category": "media",
        "description": "Upload, manage, and interact with YouTube videos and channels",
        "enabled": True,
    },
    "supabase": {
        "category": "database",
        "description": "Interact with Supabase database and authentication",
        "enabled": True,
    },
    "linkedin": {
        "category": "social",
        "description": "Post content and manage LinkedIn profile",
        "enabled": True,
    },
    "facebook": {
        "category": "social",
        "description": "Post content and manage Facebook pages",
        "enabled": True,
    },
    "stripe": {
        "category": "payment",
        "description": "Process payments and manage Stripe subscriptions",
        "enabled": True,
    },
    # Add metadata for other tools as needed
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_enabled_tools() -> dict:
    """
    Get all enabled tools.
    
    Returns:
        Dictionary of enabled tools {app_name: auth_config_id}
    """
    return ENABLED_TOOLS.copy()


def get_auth_config_id(app_name: str) -> str:
    """
    Get auth_config_id for a specific app.
    
    Args:
        app_name: Name of the app (e.g., 'gmail', 'slack')
    
    Returns:
        The auth_config_id for the app
    
    Raises:
        ValueError: If app is not in enabled tools
    """
    app_lower = app_name.lower()
    if app_lower not in ENABLED_TOOLS:
        raise ValueError(
            f"App '{app_name}' is not enabled. "
            f"Enabled apps: {list(ENABLED_TOOLS.keys())}"
        )
    return ENABLED_TOOLS[app_lower]


def is_tool_enabled(app_name: str) -> bool:
    """
    Check if a tool is enabled.
    
    Args:
        app_name: Name of the app
    
    Returns:
        True if enabled, False otherwise
    """
    return app_name.lower() in ENABLED_TOOLS


def get_tool_metadata(app_name: str) -> dict:
    """
    Get metadata for a tool.
    
    Args:
        app_name: Name of the app
    
    Returns:
        Metadata dictionary or empty dict if not found
    """
    return TOOL_METADATA.get(app_name.lower(), {})


def get_tools_by_category(category: str) -> dict:
    """
    Get all tools in a specific category.
    
    Args:
        category: Category name (e.g., 'email', 'communication')
    
    Returns:
        Dictionary of tools in that category
    """
    result = {}
    for app_name, auth_config_id in ENABLED_TOOLS.items():
        metadata = TOOL_METADATA.get(app_name, {})
        if metadata.get("category") == category:
            result[app_name] = auth_config_id
    return result
