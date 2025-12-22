"""
Provider Actions Configuration

This file defines the available actions for each Composio integration/provider.
These actions are exposed via the /api/tools/actions/{provider} endpoint.

To add actions for a new provider:
1. Add a new key in PROVIDER_ACTIONS dictionary
2. List all available action slugs from Composio
3. Provide a description for each action
"""

# ============================================
# PROVIDER ACTIONS CONFIGURATION
# ============================================

PROVIDER_ACTIONS = {
    # ================== EMAIL & COMMUNICATION ==================
    
    "gmail": [
        {"name": "GMAIL_SEND_EMAIL", "description": "Send an email"},
        {"name": "GMAIL_FETCH_EMAILS", "description": "Fetch/search emails with optional query filter"},
        {"name": "GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID", "description": "Get a specific email by message ID"},
        {"name": "GMAIL_FETCH_MESSAGE_BY_THREAD_ID", "description": "Get all messages in a thread"},
        {"name": "GMAIL_CREATE_EMAIL_DRAFT", "description": "Create an email draft"},
        {"name": "GMAIL_ADD_LABEL_TO_EMAIL", "description": "Add or remove labels from an email"},
        {"name": "GMAIL_LIST_LABELS", "description": "List all Gmail labels"},
        {"name": "GMAIL_DELETE_MESSAGE", "description": "Permanently delete an email"},
        {"name": "GMAIL_MARK_EMAIL_AS_READ", "description": "Mark an email as read"},
        {"name": "GMAIL_MARK_EMAIL_AS_UNREAD", "description": "Mark an email as unread"},
        {"name": "GMAIL_TRASH_MESSAGE", "description": "Move message to trash"},
        {"name": "GMAIL_GET_PROFILE", "description": "Get Gmail user profile information"},
    ],
    
    "slack": [
        {"name": "SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL", "description": "Send a message to a channel"},
        {"name": "SLACK_LIST_ALL_SLACK_TEAM_CHANNELS_WITH_PAGINATION", "description": "List available channels"},
        {"name": "SLACK_FETCHES_CONVERSATION_HISTORY", "description": "Get channel message history"},
        {"name": "SLACK_SEARCH_MESSAGES_IN_SLACK", "description": "Search for messages"},
        {"name": "SLACK_UPDATE_A_MESSAGE", "description": "Update an existing message"},
        {"name": "SLACK_DELETE_A_MESSAGE", "description": "Delete a message"},
        {"name": "SLACK_GET_CHANNEL_INFO", "description": "Get information about a channel"},
        {"name": "SLACK_CREATE_CHANNEL", "description": "Create a new channel"},
    ],
    
    # ================== GOOGLE SERVICES ==================
    
    "docs": [
        {"name": "GOOGLEDOCS_CREATE_DOCUMENT", "description": "Create a new Google Doc"},
        {"name": "GOOGLEDOCS_GET_DOCUMENT", "description": "Get document content"},
        {"name": "GOOGLEDOCS_UPDATE_DOCUMENT", "description": "Update document content"},
        {"name": "GOOGLEDOCS_DELETE_DOCUMENT", "description": "Delete a document"},
        {"name": "GOOGLEDOCS_INSERT_TEXT", "description": "Insert text at a specific location"},
        {"name": "GOOGLEDOCS_REPLACE_TEXT", "description": "Replace text in document"},
        {"name": "GOOGLEDOCS_FORMAT_TEXT", "description": "Format text (bold, italic, etc.)"},
    ],
    
    "sheet": [
        {"name": "GOOGLESHEETS_CREATE_SPREADSHEET", "description": "Create a new spreadsheet"},
        {"name": "GOOGLESHEETS_GET_SPREADSHEET", "description": "Get spreadsheet data"},
        {"name": "GOOGLESHEETS_UPDATE_CELL", "description": "Update cell value"},
        {"name": "GOOGLESHEETS_UPDATE_RANGE", "description": "Update a range of cells"},
        {"name": "GOOGLESHEETS_APPEND_ROW", "description": "Append a new row"},
        {"name": "GOOGLESHEETS_DELETE_ROW", "description": "Delete a row"},
        {"name": "GOOGLESHEETS_CREATE_SHEET", "description": "Create a new sheet in spreadsheet"},
        {"name": "GOOGLESHEETS_GET_VALUES", "description": "Get values from a range"},
    ],
    
    "drive": [
        {"name": "GOOGLEDRIVE_LIST_FILES", "description": "List files in Google Drive"},
        {"name": "GOOGLEDRIVE_UPLOAD_FILE", "description": "Upload a file to Drive"},
        {"name": "GOOGLEDRIVE_DOWNLOAD_FILE", "description": "Download a file from Drive"},
        {"name": "GOOGLEDRIVE_DELETE_FILE", "description": "Delete a file"},
        {"name": "GOOGLEDRIVE_CREATE_FOLDER", "description": "Create a new folder"},
        {"name": "GOOGLEDRIVE_MOVE_FILE", "description": "Move file to another folder"},
        {"name": "GOOGLEDRIVE_SHARE_FILE", "description": "Share a file with others"},
        {"name": "GOOGLEDRIVE_SEARCH_FILES", "description": "Search for files"},
        {"name": "GOOGLEDRIVE_GET_FILE_METADATA", "description": "Get file metadata"},
    ],
    
    # ================== DEVELOPMENT & VERSION CONTROL ==================
    
    "github": [
        {"name": "GITHUB_CREATE_ISSUE", "description": "Create a new issue"},
        {"name": "GITHUB_LIST_ISSUES", "description": "List repository issues"},
        {"name": "GITHUB_GET_ISSUE", "description": "Get issue details"},
        {"name": "GITHUB_UPDATE_ISSUE", "description": "Update an issue"},
        {"name": "GITHUB_CLOSE_ISSUE", "description": "Close an issue"},
        {"name": "GITHUB_CREATE_PULL_REQUEST", "description": "Create a pull request"},
        {"name": "GITHUB_LIST_PULL_REQUESTS", "description": "List pull requests"},
        {"name": "GITHUB_MERGE_PULL_REQUEST", "description": "Merge a pull request"},
        {"name": "GITHUB_CREATE_REPOSITORY", "description": "Create a new repository"},
        {"name": "GITHUB_LIST_REPOSITORIES", "description": "List user repositories"},
        {"name": "GITHUB_GET_FILE_CONTENT", "description": "Get file content from repo"},
        {"name": "GITHUB_CREATE_FILE", "description": "Create a file in repository"},
        {"name": "GITHUB_UPDATE_FILE", "description": "Update a file in repository"},
        {"name": "GITHUB_LIST_COMMITS", "description": "List repository commits"},
    ],
    
    "bitbucket": [
        {"name": "BITBUCKET_CREATE_REPOSITORY", "description": "Create a new repository"},
        {"name": "BITBUCKET_LIST_REPOSITORIES", "description": "List repositories"},
        {"name": "BITBUCKET_CREATE_PULL_REQUEST", "description": "Create a pull request"},
        {"name": "BITBUCKET_LIST_PULL_REQUESTS", "description": "List pull requests"},
        {"name": "BITBUCKET_MERGE_PULL_REQUEST", "description": "Merge a pull request"},
        {"name": "BITBUCKET_CREATE_ISSUE", "description": "Create an issue"},
        {"name": "BITBUCKET_LIST_ISSUES", "description": "List issues"},
        {"name": "BITBUCKET_GET_FILE", "description": "Get file from repository"},
    ],
    
    # ================== MEDIA ==================
    
    "youtube": [
        {"name": "YOUTUBE_UPLOAD_VIDEO", "description": "Upload a video to YouTube"},
        {"name": "YOUTUBE_LIST_VIDEOS", "description": "List channel videos"},
        {"name": "YOUTUBE_GET_VIDEO", "description": "Get video details"},
        {"name": "YOUTUBE_UPDATE_VIDEO", "description": "Update video metadata"},
        {"name": "YOUTUBE_DELETE_VIDEO", "description": "Delete a video"},
        {"name": "YOUTUBE_SEARCH_VIDEOS", "description": "Search for videos"},
        {"name": "YOUTUBE_LIST_PLAYLISTS", "description": "List channel playlists"},
        {"name": "YOUTUBE_CREATE_PLAYLIST", "description": "Create a new playlist"},
        {"name": "YOUTUBE_ADD_VIDEO_TO_PLAYLIST", "description": "Add video to playlist"},
    ],
    
    # Aliases for Google services (support both short and full names)
    "googledocs": [  # Alias for "docs"
        {"name": "GOOGLEDOCS_CREATE_DOCUMENT", "description": "Create a new Google Doc"},
        {"name": "GOOGLEDOCS_GET_DOCUMENT", "description": "Get document content"},
        {"name": "GOOGLEDOCS_UPDATE_DOCUMENT", "description": "Update document content"},
        {"name": "GOOGLEDOCS_DELETE_DOCUMENT", "description": "Delete a document"},
        {"name": "GOOGLEDOCS_INSERT_TEXT", "description": "Insert text at a specific location"},
        {"name": "GOOGLEDOCS_REPLACE_TEXT", "description": "Replace text in document"},
        {"name": "GOOGLEDOCS_FORMAT_TEXT", "description": "Format text (bold, italic, etc.)"},
    ],
    
    "googlesheets": [  # Alias for "sheet"
        {"name": "GOOGLESHEETS_CREATE_SPREADSHEET", "description": "Create a new spreadsheet"},
        {"name": "GOOGLESHEETS_GET_SPREADSHEET", "description": "Get spreadsheet data"},
        {"name": "GOOGLESHEETS_UPDATE_CELL", "description": "Update cell value"},
        {"name": "GOOGLESHEETS_UPDATE_RANGE", "description": "Update a range of cells"},
        {"name": "GOOGLESHEETS_APPEND_ROW", "description": "Append a new row"},
        {"name": "GOOGLESHEETS_DELETE_ROW", "description": "Delete a row"},
        {"name": "GOOGLESHEETS_CREATE_SHEET", "description": "Create a new sheet in spreadsheet"},
        {"name": "GOOGLESHEETS_GET_VALUES", "description": "Get values from a range"},
    ],
    
    "googledrive": [  # Alias for "drive"
        {"name": "GOOGLEDRIVE_LIST_FILES", "description": "List files in Google Drive"},
        {"name": "GOOGLEDRIVE_UPLOAD_FILE", "description": "Upload a file to Drive"},
        {"name": "GOOGLEDRIVE_DOWNLOAD_FILE", "description": "Download a file from Drive"},
        {"name": "GOOGLEDRIVE_DELETE_FILE", "description": "Delete a file"},
        {"name": "GOOGLEDRIVE_CREATE_FOLDER", "description": "Create a new folder"},
        {"name": "GOOGLEDRIVE_MOVE_FILE", "description": "Move file to another folder"},
        {"name": "GOOGLEDRIVE_SHARE_FILE", "description": "Share a file with others"},
        {"name": "GOOGLEDRIVE_SEARCH_FILES", "description": "Search for files"},
        {"name": "GOOGLEDRIVE_GET_FILE_METADATA", "description": "Get file metadata"},
    ],
    
    # ================== COMMUNICATION ==================
    
    "whatsapp": [
        {"name": "WHATSAPP_SEND_MESSAGE", "description": "Send a WhatsApp message"},
        {"name": "WHATSAPP_SEND_TEMPLATE_MESSAGE", "description": "Send a template message"},
        {"name": "WHATSAPP_SEND_MEDIA", "description": "Send media (image, video, document)"},
        {"name": "WHATSAPP_GET_MESSAGES", "description": "Get incoming messages"},
        {"name": "WHATSAPP_MARK_AS_READ", "description": "Mark message as read"},
    ],
    
    # ================== VIDEO & CONFERENCING ==================
    
    "zoom": [
        {"name": "ZOOM_CREATE_MEETING", "description": "Create a new Zoom meeting"},
        {"name": "ZOOM_LIST_MEETINGS", "description": "List all scheduled meetings"},
        {"name": "ZOOM_GET_MEETING", "description": "Get meeting details"},
        {"name": "ZOOM_UPDATE_MEETING", "description": "Update meeting details"},
        {"name": "ZOOM_DELETE_MEETING", "description": "Delete a meeting"},
        {"name": "ZOOM_START_MEETING", "description": "Start a scheduled meeting"},
        {"name": "ZOOM_END_MEETING", "description": "End an active meeting"},
        {"name": "ZOOM_LIST_RECORDINGS", "description": "List meeting recordings"},
    ],
    
    "googlemeet": [
        {"name": "GOOGLEMEET_CREATE_MEETING", "description": "Create a Google Meet meeting"},
        {"name": "GOOGLEMEET_SCHEDULE_MEETING", "description": "Schedule a meeting with calendar event"},
        {"name": "GOOGLEMEET_GET_MEETING", "description": "Get meeting details"},
        {"name": "GOOGLEMEET_UPDATE_MEETING", "description": "Update meeting details"},
        {"name": "GOOGLEMEET_DELETE_MEETING", "description": "Delete a meeting"},
    ],
    
    # ================== GOOGLE SERVICES (ADDITIONAL) ==================
    
    "googleads": [
        {"name": "GOOGLEADS_CREATE_CAMPAIGN", "description": "Create an ad campaign"},
        {"name": "GOOGLEADS_LIST_CAMPAIGNS", "description": "List all campaigns"},
        {"name": "GOOGLEADS_GET_CAMPAIGN", "description": "Get campaign details"},
        {"name": "GOOGLEADS_UPDATE_CAMPAIGN", "description": "Update campaign settings"},
        {"name": "GOOGLEADS_PAUSE_CAMPAIGN", "description": "Pause a campaign"},
        {"name": "GOOGLEADS_GET_CAMPAIGN_STATS", "description": "Get campaign statistics"},
        {"name": "GOOGLEADS_CREATE_AD_GROUP", "description": "Create an ad group"},
        {"name": "GOOGLEADS_GET_KEYWORDS", "description": "Get campaign keywords"},
    ],
    
    "googlemaps": [
        {"name": "GOOGLEMAPS_GEOCODE", "description": "Convert address to coordinates"},
        {"name": "GOOGLEMAPS_REVERSE_GEOCODE", "description": "Convert coordinates to address"},
        {"name": "GOOGLEMAPS_GET_DIRECTIONS", "description": "Get directions between locations"},
        {"name": "GOOGLEMAPS_DISTANCE_MATRIX", "description": "Calculate distances and travel times"},
        {"name": "GOOGLEMAPS_PLACES_SEARCH", "description": "Search for places"},
        {"name": "GOOGLEMAPS_PLACE_DETAILS", "description": "Get place details"},
        {"name": "GOOGLEMAPS_ELEVATION", "description": "Get elevation data"},
    ],
    
    # ================== DATABASE & BACKEND ==================
    
    "supabase": [
        {"name": "SUPABASE_INSERT_ROW", "description": "Insert a row into table"},
        {"name": "SUPABASE_SELECT_ROWS", "description": "Query rows from table"},
        {"name": "SUPABASE_UPDATE_ROW", "description": "Update a row in table"},
        {"name": "SUPABASE_DELETE_ROW", "description": "Delete a row from table"},
        {"name": "SUPABASE_EXECUTE_RPC", "description": "Execute stored procedure"},
        {"name": "SUPABASE_CREATE_USER", "description": "Create authentication user"},
        {"name": "SUPABASE_UPLOAD_FILE", "description": "Upload file to storage"},
        {"name": "SUPABASE_DOWNLOAD_FILE", "description": "Download file from storage"},
    ],
    
    # ================== SOCIAL MEDIA ==================
    
    "linkedin": [
        {"name": "LINKEDIN_CREATE_POST", "description": "Create a LinkedIn post"},
        {"name": "LINKEDIN_SHARE_ARTICLE", "description": "Share an article"},
        {"name": "LINKEDIN_GET_PROFILE", "description": "Get profile information"},
        {"name": "LINKEDIN_UPDATE_PROFILE", "description": "Update profile details"},
        {"name": "LINKEDIN_SEND_MESSAGE", "description": "Send a message to connection"},
        {"name": "LINKEDIN_GET_CONNECTIONS", "description": "Get list of connections"},
        {"name": "LINKEDIN_CREATE_COMPANY_POST", "description": "Post on company page"},
    ],
    
    "facebook": [
        {"name": "FACEBOOK_CREATE_POST", "description": "Create a post on page"},
        {"name": "FACEBOOK_UPLOAD_PHOTO", "description": "Upload a photo"},
        {"name": "FACEBOOK_UPLOAD_VIDEO", "description": "Upload a video"},
        {"name": "FACEBOOK_GET_PAGE_INSIGHTS", "description": "Get page analytics"},
        {"name": "FACEBOOK_GET_POSTS", "description": "Get page posts"},
        {"name": "FACEBOOK_DELETE_POST", "description": "Delete a post"},
        {"name": "FACEBOOK_SEND_MESSAGE", "description": "Send message via Messenger"},
        {"name": "FACEBOOK_CREATE_AD", "description": "Create a Facebook ad"},
    ],
    
    # ================== PAYMENT & FINANCE ==================
    
    "stripe": [
        {"name": "STRIPE_CREATE_CUSTOMER", "description": "Create a new customer"},
        {"name": "STRIPE_GET_CUSTOMER", "description": "Get customer details"},
        {"name": "STRIPE_CREATE_PAYMENT_INTENT", "description": "Create payment intent"},
        {"name": "STRIPE_CAPTURE_PAYMENT", "description": "Capture a payment"},
        {"name": "STRIPE_REFUND_PAYMENT", "description": "Refund a payment"},
        {"name": "STRIPE_CREATE_SUBSCRIPTION", "description": "Create a subscription"},
        {"name": "STRIPE_CANCEL_SUBSCRIPTION", "description": "Cancel a subscription"},
        {"name": "STRIPE_LIST_INVOICES", "description": "List customer invoices"},
        {"name": "STRIPE_CREATE_PRODUCT", "description": "Create a product"},
        {"name": "STRIPE_GET_BALANCE", "description": "Get account balance"},
    ],
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_provider_actions(provider: str) -> list:
    """
    Get actions for a specific provider.
    
    Args:
        provider: Provider name (e.g., 'gmail', 'slack')
    
    Returns:
        List of action dictionaries with 'name' and 'description'
    
    Raises:
        KeyError: If provider is not found
    """
    provider_lower = provider.lower()
    if provider_lower not in PROVIDER_ACTIONS:
        raise KeyError(f"Provider '{provider}' not found in actions configuration")
    return PROVIDER_ACTIONS[provider_lower]


def get_all_providers() -> list:
    """
    Get list of all providers that have actions defined.
    
    Returns:
        List of provider names
    """
    return list(PROVIDER_ACTIONS.keys())


def is_provider_supported(provider: str) -> bool:
    """
    Check if a provider has actions defined.
    
    Args:
        provider: Provider name
    
    Returns:
        True if provider is supported, False otherwise
    """
    return provider.lower() in PROVIDER_ACTIONS


def get_action_count(provider: str) -> int:
    """
    Get number of actions available for a provider.
    
    Args:
        provider: Provider name
    
    Returns:
        Number of actions
    """
    try:
        return len(get_provider_actions(provider))
    except KeyError:
        return 0


def search_actions(query: str, provider: str = None) -> list:
    """
    Search for actions by name or description.
    
    Args:
        query: Search query
        provider: Optional provider to limit search
    
    Returns:
        List of matching actions with provider info
    """
    results = []
    query_lower = query.lower()
    
    providers_to_search = [provider] if provider else get_all_providers()
    
    for prov in providers_to_search:
        try:
            actions = get_provider_actions(prov)
            for action in actions:
                if (query_lower in action["name"].lower() or 
                    query_lower in action["description"].lower()):
                    results.append({
                        "provider": prov,
                        **action
                    })
        except KeyError:
            continue
    
    return results
