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
        # Email Management
        {"name": "GMAIL_SEND_EMAIL", "description": "Send Email - Sends an email via Gmail API (supports HTML, attachments, To/Cc/Bcc)"},
        {"name": "GMAIL_FETCH_EMAILS", "description": "Fetch emails - Fetches a list of email messages with filtering, pagination, and full content"},
        {"name": "GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID", "description": "Fetch message by message ID - Fetches a specific email by its ID"},
        {"name": "GMAIL_FETCH_MESSAGE_BY_THREAD_ID", "description": "Fetch Message by Thread ID - Retrieves messages from a Gmail thread"},
        {"name": "GMAIL_DELETE_MESSAGE", "description": "Delete message - Permanently deletes a specific email message by its ID"},
        {"name": "GMAIL_FORWARD_MESSAGE", "description": "Forward email message - Forward an existing message to recipients"},
        {"name": "GMAIL_REPLY_TO_THREAD", "description": "Reply to email thread - Sends a reply within a specific Gmail thread"},
        {"name": "GMAIL_MOVE_TO_TRASH", "description": "Move to Trash - Moves an existing email message to the trash"},
        {"name": "GMAIL_BATCH_DELETE_MESSAGES", "description": "Batch delete Gmail messages - Permanently delete multiple emails in bulk"},
        {"name": "GMAIL_BATCH_MODIFY_MESSAGES", "description": "Batch modify Gmail messages - Modify labels on up to 1,000 messages"},
        
        # Draft Management
        {"name": "GMAIL_CREATE_EMAIL_DRAFT", "description": "Create email draft - Creates a Gmail draft with To/Cc/Bcc, subject, body, attachments, threading"},
        # {"name": "GMAIL_UPDATE_DRAFT", "description": "Update draft - Updates an existing email draft"},
        {"name": "GMAIL_DELETE_DRAFT", "description": "Delete Draft - Permanently deletes a specific Gmail draft by ID"},
        {"name": "GMAIL_SEND_DRAFT", "description": "Send Draft - Sends the specified existing draft to recipients"},
        {"name": "GMAIL_LIST_DRAFTS", "description": "List drafts - Retrieves a paginated list of email drafts with full details"},
        
        # Label Operations
        {"name": "GMAIL_ADD_LABEL_TO_EMAIL", "description": "Modify email labels - Adds and/or removes specified Gmail labels for a message"},
        {"name": "GMAIL_CREATE_LABEL", "description": "Create label - Creates a new label with a unique name in Gmail account"},
        {"name": "GMAIL_REMOVE_LABEL", "description": "Remove label - Permanently deletes a specific user-created Gmail label by ID"},
        {"name": "GMAIL_LIST_LABELS", "description": "List Gmail labels - Retrieves all system and user-created labels"},
        {"name": "GMAIL_PATCH_LABEL", "description": "Patch Label - Patches the specified label"},
        
        # Thread Operations
        {"name": "GMAIL_LIST_THREADS", "description": "List threads - Retrieves email threads with filtering and pagination"},
        {"name": "GMAIL_MODIFY_THREAD_LABELS", "description": "Modify thread labels - Adds or removes label IDs from a Gmail thread"},
        
        # Attachments
        {"name": "GMAIL_GET_ATTACHMENT", "description": "Get Gmail attachment - Retrieves a specific attachment by ID from a message"},
        
        # Contacts & Profile
        {"name": "GMAIL_GET_CONTACTS", "description": "Get contacts - Fetches contacts (connections) with field selection and pagination"},
        {"name": "GMAIL_GET_PEOPLE", "description": "Get People - Retrieves person details or lists Other Contacts"},
        {"name": "GMAIL_SEARCH_PEOPLE", "description": "Search People - Searches contacts by name, email, phone, organization"},
        {"name": "GMAIL_GET_PROFILE", "description": "Get Profile - Retrieves Gmail profile information (email, message/thread totals, history ID)"},
        
        # History
        {"name": "GMAIL_LIST_HISTORY", "description": "List Gmail history - List mailbox change history since a known startHistoryId"},
    ],
    
    "slack": [
        # Messages (Essential)
        {"name": "SLACK_SEND_MESSAGE", "description": "Send a message to a channel"},
        {"name": "SLACK_UPDATES_A_SLACK_MESSAGE", "description": "Update a message - Updates an existing message"},
        {"name": "SLACK_DELETES_A_MESSAGE_FROM_A_CHAT", "description": "Delete a message from a chat"},
        {"name": "SLACK_SCHEDULE_MESSAGE", "description": "Schedule a message - Schedule message for later delivery"},
        {"name": "SLACK_RETRIEVE_MESSAGE_PERMALINK_URL", "description": "Get permalink to a message"},
        {"name": "SLACK_SEND_EPHEMERAL_MESSAGE", "description": "Send ephemeral message - Visible only to one user"},
        
        # Channels & Conversations (Essential)
        {"name": "SLACK_CREATE_CHANNEL", "description": "Create channel - Initiates a public or private channel"},
        {"name": "SLACK_LIST_ALL_CHANNELS", "description": "List all channels"},
        {"name": "SLACK_LIST_CONVERSATIONS", "description": "List conversations with pagination"},
        {"name": "SLACK_FETCH_CONVERSATION_HISTORY", "description": "Fetch conversation history"},
        {"name": "SLACK_RETRIEVE_CONVERSATION_INFORMATION", "description": "Get information about a channel"},
        {"name": "SLACK_ARCHIVE_A_SLACK_CONVERSATION", "description": "Archive a Slack conversation"},
        {"name": "SLACK_UNARCHIVE_CHANNEL", "description": "Unarchive a channel"},
        {"name": "SLACK_INVITE_USER_TO_CHANNEL", "description": "Invite users to a channel"},
        {"name": "SLACK_REMOVE_A_USER_FROM_A_CONVERSATION", "description": "Remove a user from a channel"},
        {"name": "SLACK_JOIN_AN_EXISTING_CONVERSATION", "description": "Join an existing conversation"},
        {"name": "SLACK_LEAVE_A_CONVERSATION", "description": "Leave a conversation"},
        {"name": "SLACK_RENAME_A_CONVERSATION", "description": "Rename a conversation"},
        {"name": "SLACK_SET_THE_TOPIC_OF_A_CONVERSATION", "description": "Set conversation topic"},
        {"name": "SLACK_SET_A_CONVERSATION_S_PURPOSE", "description": "Set conversation purpose"},
        {"name": "SLACK_OPEN_DM", "description": "Open a direct message"},
        
        # Reactions (Essential)
        {"name": "SLACK_ADD_REACTION_TO_AN_ITEM", "description": "Add reaction to message - Add emoji reaction"},
        {"name": "SLACK_REMOVE_REACTION_FROM_ITEM", "description": "Remove a reaction from an item"},
        {"name": "SLACK_FETCH_ITEM_REACTIONS", "description": "Get reactions for an item"},
        {"name": "SLACK_LIST_USER_REACTIONS", "description": "List reactions by user"},
        
        # Search (Essential)
        {"name": "SLACK_SEARCH_MESSAGES", "description": "Search messages in Slack"},
        {"name": "SLACK_SEARCH_ALL", "description": "Search all - Search messages and files"},
        
        # Users (Essential)
        {"name": "SLACK_RETRIEVE_DETAILED_USER_INFORMATION", "description": "Get user information"},
        {"name": "SLACK_LIST_WORKSPACE_USERS", "description": "List all users in workspace"},
        {"name": "SLACK_GET_USER_PRESENCE_INFO", "description": "Get user presence status"},
        {"name": "SLACK_MANUALLY_SET_USER_PRESENCE", "description": "Set user presence status"},
        {"name": "SLACK_FIND_USER_BY_EMAIL_ADDRESS", "description": "Find user by email"},
        
        # User Profile (Essential)
        {"name": "SLACK_RETRIEVE_USER_PROFILE_INFORMATION", "description": "Get user profile"},
        {"name": "SLACK_SET_SLACK_USER_PROFILE_INFORMATION", "description": "Update user profile"},
        {"name": "SLACK_SET_STATUS", "description": "Set user status"},
        {"name": "SLACK_CLEAR_STATUS", "description": "Clear Slack status"},
        
        # Files (Essential)
        {"name": "SLACK_UPLOAD_OR_CREATE_A_FILE_IN_SLACK", "description": "Upload or create a file"},
        {"name": "SLACK_DELETE_A_FILE_BY_ID", "description": "Delete a file by ID - Permanently delete file"},
        {"name": "SLACK_RETRIEVE_DETAILED_INFORMATION_ABOUT_A_FILE", "description": "Get info on a file"},
        {"name": "SLACK_LIST_FILES_WITH_FILTERS_IN_SLACK", "description": "List files in workspace"},
        {"name": "SLACK_ENABLE_PUBLIC_SHARING_OF_A_FILE", "description": "Share file public url - Enable public sharing"},
        {"name": "SLACK_REVOKE_PUBLIC_SHARING_ACCESS_FOR_A_FILE", "description": "Revoke public URL for file"},
        
        # Reminders (Essential)
        {"name": "SLACK_CREATE_A_REMINDER", "description": "Create a reminder"},
        {"name": "SLACK_DELETE_A_SLACK_REMINDER", "description": "Delete a Slack reminder"},
        {"name": "SLACK_LIST_REMINDERS", "description": "List reminders"},
        {"name": "SLACK_GET_REMINDER_INFORMATION", "description": "Get info about a reminder"},
        {"name": "SLACK_MARK_REMINDER_AS_COMPLETE", "description": "Mark a reminder as complete"},
        
        # Pins (Essential)
        {"name": "SLACK_PINS_AN_ITEM_TO_A_CHANNEL", "description": "Pin an item to a channel"},
        {"name": "SLACK_UNPIN_ITEM_FROM_CHANNEL", "description": "Remove a pinned item from a channel"},
        {"name": "SLACK_LISTS_PINNED_ITEMS_IN_A_CHANNEL", "description": "List pinned items in a channel"},
        
        # Stars (Essential)
        {"name": "SLACK_ADD_A_STAR_TO_AN_ITEM", "description": "Add a star to an item"},
        {"name": "SLACK_REMOVE_A_STAR_FROM_AN_ITEM", "description": "Remove a star from an item"},
        {"name": "SLACK_LIST_STARRED_ITEMS", "description": "List starred items"},
        
        # Team & Admin (Essential)
        {"name": "SLACK_FETCH_TEAM_INFO", "description": "Get team information"},
        {"name": "SLACK_RETRIEVE_CONVERSATION_MEMBERS_LIST", "description": "Get conversation members"},
        {"name": "SLACK_RETRIEVE_TEAM_PROFILE_DETAILS", "description": "Get team profile"},
    ],
    
    # ================== GOOGLE SERVICES ==================
    
    "googlebigquery": [
        {"name": "GOOGLEBIGQUERY_QUERY", "description": "Run a SQL query in BigQuery"},
        # Note: All BigQuery operations must be performed via SQL
    ],
    
    "googledocs": [
        # Document Operations (Essential)
        {"name": "GOOGLEDOCS_CREATE_DOCUMENT", "description": "Create a document - Creates a new Google Docs document"},
        {"name": "GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN", "description": "Create Document Markdown - Creates a new document with Markdown content"},
        {"name": "GOOGLEDOCS_COPY_DOCUMENT", "description": "Copy Google Document - Create a duplicate of an existing document"},
        {"name": "GOOGLEDOCS_GET_DOCUMENT_BY_ID", "description": "Get document by id - Retrieve an existing document by its ID"},
        {"name": "GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT", "description": "Update existing document - Modify document content"},
        {"name": "GOOGLEDOCS_SEARCH_DOCUMENTS", "description": "Search documents - Find documents by query"},
        
        # Text Operations (Essential)
        {"name": "GOOGLEDOCS_INSERT_TEXT_ACTION", "description": "Insert text - Insert text at a specific location"},
        {"name": "GOOGLEDOCS_REPLACE_ALL_TEXT", "description": "Replace All Text - Replace all instances of text in the document"},
        {"name": "GOOGLEDOCS_DELETE_CONTENT_RANGE", "description": "Delete Content Range in Document - Remove a specific portion of text"},
        
        # Formatting (Essential)
        {"name": "GOOGLEDOCS_CREATE_PARAGRAPH_BULLETS", "description": "Create Paragraph Bullets - Add bullets to paragraphs"},
        {"name": "GOOGLEDOCS_DELETE_PARAGRAPH_BULLETS", "description": "Delete Paragraph Bullets - Remove bullet formatting from paragraphs"},
        
        # Tables (Essential)
        {"name": "GOOGLEDOCS_INSERT_TABLE_ACTION", "description": "Insert Table in Google Doc - Add a new table to the document"},
        {"name": "GOOGLEDOCS_DELETE_TABLE", "description": "Delete Table - Remove an entire table from the document"},
        {"name": "GOOGLEDOCS_DELETE_TABLE_ROW", "description": "Delete Table Row - Remove a row from a table"},
        {"name": "GOOGLEDOCS_DELETE_TABLE_COLUMN", "description": "Delete Table Column - Remove a column from a table"},
        {"name": "GOOGLEDOCS_INSERT_TABLE_COLUMN", "description": "Insert Table Column - Add a column to a table"},
        
        # Images (Essential)
        {"name": "GOOGLEDOCS_INSERT_INLINE_IMAGE", "description": "Insert Inline Image - Add an image at a specified location"},
        {"name": "GOOGLEDOCS_REPLACE_IMAGE", "description": "Replace Image - Replace an existing image with a new one"},
        
        # Other (Essential)
        {"name": "GOOGLEDOCS_INSERT_PAGE_BREAK", "description": "Insert Page Break - Start new content on a fresh page"},
    ],
    
    "googlesheets": [
        # Spreadsheet Operations (Essential)
        {"name": "GOOGLESHEETS_CREATE_GOOGLE_SHEET1", "description": "Create a new spreadsheet"},
        {"name": "GOOGLESHEETS_GET_SPREADSHEET_INFO", "description": "Get spreadsheet information"},
        {"name": "GOOGLESHEETS_SEARCH_SPREADSHEETS", "description": "Search for spreadsheets"},
        
        # Sheet Operations (Essential)
        {"name": "GOOGLESHEETS_ADD_SHEET", "description": "Add Sheet - Create a new tab within spreadsheet"},
        {"name": "GOOGLESHEETS_DELETE_SHEET", "description": "Delete a sheet"},
        {"name": "GOOGLESHEETS_GET_SHEET_NAMES", "description": "Get all sheet names in spreadsheet"},
        {"name": "GOOGLESHEETS_FIND_WORKSHEET_BY_TITLE", "description": "Find worksheet by title"},
        {"name": "GOOGLESHEETS_UPDATE_SHEET_PROPERTIES", "description": "Update sheet properties"},
        
        # Data Operations (Essential)
        {"name": "GOOGLESHEETS_VALUES_GET", "description": "Get values from a range"},
        {"name": "GOOGLESHEETS_VALUES_UPDATE", "description": "Update values in range"},
        {"name": "GOOGLESHEETS_SPREADSHEETS_VALUES_APPEND", "description": "Append values to sheet"},
        {"name": "GOOGLESHEETS_BATCH_GET", "description": "Batch get - Retrieve data from multiple cell ranges"},
        {"name": "GOOGLESHEETS_BATCH_UPDATE", "description": "Batch update - Update specified range with values"},
        {"name": "GOOGLESHEETS_CLEAR_VALUES", "description": "Clear values from range"},
        
        # Row/Column Operations (Essential)
        {"name": "GOOGLESHEETS_CREATE_SPREADSHEET_ROW", "description": "Create a new row"},
        {"name": "GOOGLESHEETS_CREATE_SPREADSHEET_COLUMN", "description": "Create a new column"},
        {"name": "GOOGLESHEETS_INSERT_DIMENSION", "description": "Insert rows or columns"},
        {"name": "GOOGLESHEETS_DELETE_DIMENSION", "description": "Delete rows or columns"},
        {"name": "GOOGLESHEETS_APPEND_DIMENSION", "description": "Append Dimension - Add empty rows or columns"},
        {"name": "GOOGLESHEETS_LOOKUP_SPREADSHEET_ROW", "description": "Lookup row by criteria"},
        {"name": "GOOGLESHEETS_UPSERT_ROWS", "description": "Upsert rows - Insert or update"},
        
        # Data Analysis (Essential)
        {"name": "GOOGLESHEETS_AGGREGATE_COLUMN_DATA", "description": "Aggregate Column Data - Perform math operations"},
        {"name": "GOOGLESHEETS_FIND_REPLACE", "description": "Find and replace in sheet"},
        {"name": "GOOGLESHEETS_EXECUTE_SQL", "description": "Execute SQL query on sheet"},
        {"name": "GOOGLESHEETS_QUERY_TABLE", "description": "Query table with filters"},
        
        # Formatting (Essential)
        {"name": "GOOGLESHEETS_FORMAT_CELL", "description": "Format cells"},
        
        # Advanced (Essential)
        {"name": "GOOGLESHEETS_CREATE_CHART", "description": "Create chart"},
    ],
    
    "googledrive": [
        # File Operations (Essential)
        {"name": "GOOGLEDRIVE_CREATE_FILE", "description": "Create File or Folder - Create with metadata"},
        {"name": "GOOGLEDRIVE_CREATE_FILE_FROM_TEXT", "description": "Create a File from Text - Up to 10MB"},
        {"name": "GOOGLEDRIVE_UPLOAD_FILE", "description": "Upload a file to Drive"},
        {"name": "GOOGLEDRIVE_DOWNLOAD_FILE", "description": "Download a file from Drive"},
        {"name": "GOOGLEDRIVE_DOWNLOAD_FILE_OPERATION", "description": "Download file operation"},
        {"name": "GOOGLEDRIVE_COPY_FILE", "description": "Copy file - Duplicate an existing file"},
        {"name": "GOOGLEDRIVE_GOOGLE_DRIVE_DELETE_FOLDER_OR_FILE_ACTION", "description": "Delete a file or folder"},
        {"name": "GOOGLEDRIVE_MOVE_FILE", "description": "Move file to another folder"},
        {"name": "GOOGLEDRIVE_EDIT_FILE", "description": "Edit file content"},
        
        # Folder Operations (Essential)
        {"name": "GOOGLEDRIVE_CREATE_FOLDER", "description": "Create a folder"},
        {"name": "GOOGLEDRIVE_FIND_FOLDER", "description": "Find folder by name or criteria"},
        
        # File Access (Essential)
        {"name": "GOOGLEDRIVE_GET_FILE_METADATA", "description": "Get file metadata"},
        {"name": "GOOGLEDRIVE_LIST_FILES", "description": "List files in Google Drive"},
        {"name": "GOOGLEDRIVE_FIND_FILE", "description": "Find file by name or criteria"},
        {"name": "GOOGLEDRIVE_PARSE_FILE", "description": "Parse file content"},
        
        # Sharing & Permissions (Essential)
        {"name": "GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE", "description": "Add file sharing preference - Grant role to user/group"},
        {"name": "GOOGLEDRIVE_LIST_PERMISSIONS", "description": "List file permissions"},
        {"name": "GOOGLEDRIVE_GET_PERMISSION", "description": "Get specific permission details"},
        {"name": "GOOGLEDRIVE_UPDATE_PERMISSION", "description": "Update permission"},
        {"name": "GOOGLEDRIVE_DELETE_PERMISSION", "description": "Delete permission"},
        
        # Comments (Essential)
        {"name": "GOOGLEDRIVE_CREATE_COMMENT", "description": "Create Comment - Add comment to file"},
        {"name": "GOOGLEDRIVE_LIST_COMMENTS", "description": "List comments on file"},
        {"name": "GOOGLEDRIVE_GET_COMMENT", "description": "Get specific comment"},
        {"name": "GOOGLEDRIVE_UPDATE_COMMENT", "description": "Update a comment"},
        {"name": "GOOGLEDRIVE_DELETE_COMMENT", "description": "Delete a comment"},
        {"name": "GOOGLEDRIVE_CREATE_REPLY", "description": "Create Reply - Reply to a comment"},
        
        # Shared Drives (Essential)
        {"name": "GOOGLEDRIVE_CREATE_DRIVE", "description": "Create Shared Drive"},
        {"name": "GOOGLEDRIVE_LIST_SHARED_DRIVES", "description": "List shared drives"},
        {"name": "GOOGLEDRIVE_GET_DRIVE", "description": "Get shared drive details"},
        {"name": "GOOGLEDRIVE_UPDATE_DRIVE", "description": "Update shared drive"},
        {"name": "GOOGLEDRIVE_DELETE_DRIVE", "description": "Delete shared drive"},
        
        # Trash & Revisions (Essential)
        {"name": "GOOGLEDRIVE_UNTRASH_FILE", "description": "Restore file from trash"},
        {"name": "GOOGLEDRIVE_EMPTY_TRASH", "description": "Empty trash permanently"},
        {"name": "GOOGLEDRIVE_LIST_REVISIONS", "description": "List file revisions"},
        {"name": "GOOGLEDRIVE_GET_REVISION", "description": "Get specific file revision"},
    ],
    
    # ================== MEDIA ==================
    
    "youtube": [
        # Video Operations (Essential)
        {"name": "YOUTUBE_UPLOAD_VIDEO", "description": "Upload a video to YouTube"},
        {"name": "YOUTUBE_VIDEO_DETAILS", "description": "Get video details"},
        {"name": "YOUTUBE_GET_VIDEO_DETAILS_BATCH", "description": "Get details for multiple videos"},
        {"name": "YOUTUBE_UPDATE_VIDEO", "description": "Update video metadata"},
        {"name": "YOUTUBE_UPDATE_THUMBNAIL", "description": "Update video thumbnail"},
        
        # Search (Essential)
        {"name": "YOUTUBE_SEARCH_YOU_TUBE", "description": "Search for videos on YouTube"},
        
        # Channel Operations (Essential)
        {"name": "YOUTUBE_GET_CHANNEL_STATISTICS", "description": "Get channel statistics"},
        {"name": "YOUTUBE_GET_CHANNEL_ID_BY_HANDLE", "description": "Get channel ID by handle"},
        {"name": "YOUTUBE_GET_CHANNEL_ACTIVITIES", "description": "Get channel activities"},
        {"name": "YOUTUBE_LIST_CHANNEL_VIDEOS", "description": "List videos from a channel"},
        {"name": "YOUTUBE_SUBSCRIBE_CHANNEL", "description": "Subscribe to a channel"},
        
        # Playlists (Essential)
        {"name": "YOUTUBE_LIST_USER_PLAYLISTS", "description": "List user playlists"},
        {"name": "YOUTUBE_LIST_PLAYLIST_ITEMS", "description": "List items in a playlist"},
        
        # Subscriptions (Essential)
        {"name": "YOUTUBE_LIST_USER_SUBSCRIPTIONS", "description": "List user subscriptions"},
        
        # Captions (Essential)
        {"name": "YOUTUBE_LIST_CAPTION_TRACK", "description": "List caption tracks"},
        {"name": "YOUTUBE_LOAD_CAPTIONS", "description": "Load captions for video"},
    ],
    
    # ==================COMMUNICATION ==================
    
    "whatsapp": [
        # Messages (Essential)
        {"name": "WHATSAPP_SEND_MESSAGE", "description": "Send a WhatsApp message"},
        {"name": "WHATSAPP_SEND_REPLY", "description": "Reply to a message"},
        {"name": "WHATSAPP_SEND_TEMPLATE_MESSAGE", "description": "Send a template message"},
        
        # Media (Essential)
        {"name": "WHATSAPP_SEND_MEDIA", "description": "Send media (image, video, document)"},
        {"name": "WHATSAPP_SEND_MEDIA_BY_ID", "description": "Send media by media ID"},
        {"name": "WHATSAPP_UPLOAD_MEDIA", "description": "Upload media file"},
        {"name": "WHATSAPP_GET_MEDIA", "description": "Get media from message"},
        {"name": "WHATSAPP_GET_MEDIA_INFO", "description": "Get media information"},
        
        # Interactive Messages (Essential)
        {"name": "WHATSAPP_SEND_INTERACTIVE_BUTTONS", "description": "Send interactive button message"},
        {"name": "WHATSAPP_SEND_INTERACTIVE_LIST", "description": "Send interactive list message"},
        {"name": "WHATSAPP_SEND_LOCATION", "description": "Send location"},
        {"name": "WHATSAPP_SEND_CONTACTS", "description": "Send contact card"},
        
        # Templates (Essential)
        {"name": "WHATSAPP_CREATE_MESSAGE_TEMPLATE", "description": "Create message template"},
        {"name": "WHATSAPP_GET_MESSAGE_TEMPLATES", "description": "Get message templates"},
        {"name": "WHATSAPP_GET_TEMPLATE_STATUS", "description": "Get template status"},
        {"name": "WHATSAPP_DELETE_MESSAGE_TEMPLATE", "description": "Delete message template"},
        
        # Business Profile (Essential)
        {"name": "WHATSAPP_GET_BUSINESS_PROFILE", "description": "Get business profile"},
        
        # Phone Numbers (Essential)
        {"name": "WHATSAPP_GET_PHONE_NUMBER", "description": "Get phone number details"},
        {"name": "WHATSAPP_GET_PHONE_NUMBERS", "description": "Get all phone numbers"},
    ],
    
    # ================== VIDEO & CONFERENCING ==================
    
    "zoom": [
        # Meetings (Essential)
        {"name": "ZOOM_CREATE_A_MEETING", "description": "Create a new Zoom meeting"},
        {"name": "ZOOM_LIST_MEETINGS", "description": "List all scheduled meetings"},
        {"name": "ZOOM_GET_A_MEETING", "description": "Get meeting details"},
        {"name": "ZOOM_UPDATE_A_MEETING", "description": "Update meeting details"},
        {"name": "ZOOM_GET_A_MEETING_SUMMARY", "description": "Get meeting summary"},
        
        # Participants (Essential)
        {"name": "ZOOM_GET_PAST_MEETING_PARTICIPANTS", "description": "Get past meeting participants"},
        {"name": "ZOOM_ADD_A_MEETING_REGISTRANT", "description": "Add a meeting registrant"},
        
        # Webinars (Essential)
        {"name": "ZOOM_GET_A_WEBINAR", "description": "Get webinar details"},
        {"name": "ZOOM_LIST_WEBINARS", "description": "List webinars"},
        {"name": "ZOOM_LIST_WEBINAR_PARTICIPANTS", "description": "List webinar participants"},
        {"name": "ZOOM_ADD_A_WEBINAR_REGISTRANT", "description": "Add a webinar registrant"},
        
        # Recordings (Essential)
        {"name": "ZOOM_LIST_ALL_RECORDINGS", "description": "List all meeting recordings"},
        {"name": "ZOOM_GET_MEETING_RECORDINGS", "description": "Get meeting recording details"},
        {"name": "ZOOM_DELETE_MEETING_RECORDINGS", "description": "Delete meeting recordings"},
        {"name": "ZOOM_LIST_ARCHIVED_FILES", "description": "List archived recording files"},
        
        # Devices & Reports (Essential)
        {"name": "ZOOM_LIST_DEVICES", "description": "List Zoom devices"},
        {"name": "ZOOM_GET_DAILY_USAGE_REPORT", "description": "Get daily usage report"},
    ],
    
    "googlemeet": [
        # Meetings (Essential)
        {"name": "GOOGLEMEET_CREATE_MEET", "description": "Create a Google Meet meeting"},
        {"name": "GOOGLEMEET_GET_MEET", "description": "Get meeting details"},
        {"name": "GOOGLEMEET_UPDATE_SPACE", "description": "Update meeting space"},
        {"name": "GOOGLEMEET_END_ACTIVE_CONFERENCE", "description": "End an active meeting"},
        
        # Conference Records (Essential)
        {"name": "GOOGLEMEET_LIST_CONFERENCE_RECORDS", "description": "List conference records"},
        {"name": "GOOGLEMEET_GET_CONFERENCE_RECORD_FOR_MEET", "description": "Get conference record for meeting"},
        
        # Recordings & Transcripts (Essential)
        {"name": "GOOGLEMEET_GET_RECORDINGS_BY_CONFERENCE_RECORD_ID", "description": "Get recordings by conference record ID"},
        {"name": "GOOGLEMEET_GET_TRANSCRIPTS_BY_CONFERENCE_RECORD_ID", "description": "Get transcripts by conference record ID"},
        
        # Participants (Essential)
        {"name": "GOOGLEMEET_LIST_PARTICIPANT_SESSIONS", "description": "List participant sessions"},
        {"name": "GOOGLEMEET_GET_PARTICIPANT_SESSION", "description": "Get participant session details"},
    ],
    
    # ================== GOOGLE SERVICES (ADDITIONAL) ==================
   
    "googleads": [
        # Campaigns (Essential)
        {"name": "GOOGLEADS_GET_CAMPAIGN_BY_ID", "description": "Get campaign by ID"},
        {"name": "GOOGLEADS_GET_CAMPAIGN_BY_NAME", "description": "Get campaign by name"},
        
        # Customer Lists (Essential)
        {"name": "GOOGLEADS_CREATE_CUSTOMER_LIST", "description": "Create a customer list"},
        {"name": "GOOGLEADS_GET_CUSTOMER_LISTS", "description": "Get all customer lists"},
        {"name": "GOOGLEADS_ADD_OR_REMOVE_TO_CUSTOMER_LIST", "description": "Add or remove users from customer list"},
    ],
    
    "googlemaps": [
        # Geocoding (Essential)
        {"name": "GOOGLE_MAPS_GEOCODE_ADDRESS", "description": "Convert address to coordinates"},
        {"name": "GOOGLE_MAPS_GEOCODE_LOCATION", "description": "Convert coordinates to address (reverse geocoding)"},
        {"name": "GOOGLE_MAPS_GEOCODE_PLACE", "description": "Geocode a place"},
        {"name": "GOOGLE_MAPS_GEOCODING_API", "description": "Geocoding API - Convert addresses to coordinates"},
        
        # Directions & Routes (Essential)
        {"name": "GOOGLE_MAPS_GET_DIRECTION", "description": "Get directions between locations"},
        {"name": "GOOGLE_MAPS_GET_ROUTE", "description": "Get route information"},
        {"name": "GOOGLE_MAPS_DISTANCE_MATRIX_API", "description": "Calculate distances and travel times"},
        {"name": "GOOGLE_MAPS_COMPUTE_ROUTE_MATRIX", "description": "Compute route matrix"},
        
        # Places (Essential)
        {"name": "GOOGLE_MAPS_GET_PLACE_DETAILS", "description": "Get place details"},
        {"name": "GOOGLE_MAPS_NEARBY_SEARCH", "description": "Search for nearby places"},
        {"name": "GOOGLE_MAPS_TEXT_SEARCH", "description": "Text search for places"},
        {"name": "GOOGLE_MAPS_PLACE_PHOTO", "description": "Get place photos"},
        {"name": "GOOGLE_MAPS_AUTOCOMPLETE", "description": "Autocomplete place search"},
        
        # Location (Essential)
        {"name": "GOOGLE_MAPS_GEOLOCATE", "description": "Geolocate device position"},
    ],
    
    # ================== DATABASE & BACKEND ==================
    
    "supabase": [
        # Database Operations (Essential)
        {"name": "SUPABASE_BETA_RUN_SQL_QUERY", "description": "Run SQL query on database"},
        {"name": "SUPABASE_SELECT_FROM_TABLE", "description": "Query rows from table"},
        {"name": "SUPABASE_LIST_TABLES", "description": "List all tables"},
        {"name": "SUPABASE_GET_TABLE_SCHEMAS", "description": "Get table schemas"},
        
        # Projects (Essential)
        {"name": "SUPABASE_CREATE_A_PROJECT", "description": "Create a new project"},
        {"name": "SUPABASE_LIST_ALL_PROJECTS", "description": "List all projects"},
        {"name": "SUPABASE_DELETES_THE_GIVEN_PROJECT", "description": "Delete a project"},
        {"name": "SUPABASE_GET_PROJECT_UPGRADE_STATUS", "description": "Get project upgrade status"},
        {"name": "SUPABASE_GETS_PROJECT_S_SERVICE_HEALTH_STATUS", "description": "Get project service health status"},
        
        # Functions (Essential)
        {"name": "SUPABASE_CREATE_A_FUNCTION", "description": "Create a function"},
        {"name": "SUPABASE_LIST_ALL_FUNCTIONS", "description": "List all functions"},
        {"name": "SUPABASE_RETRIEVE_A_FUNCTION", "description": "Retrieve a function"},
        {"name": "SUPABASE_UPDATE_A_FUNCTION", "description": "Update a function"},
        {"name": "SUPABASE_DELETE_A_FUNCTION", "description": "Delete a function"},
        {"name": "SUPABASE_DEPLOY_FUNCTION", "description": "Deploy function"},
        {"name": "SUPABASE_GENERATE_TYPE_SCRIPT_TYPES", "description": "Generate TypeScript types"},
        
        # Organizations (Essential)
        {"name": "SUPABASE_CREATE_AN_ORGANIZATION", "description": "Create an organization"},
        {"name": "SUPABASE_LIST_ALL_ORGANIZATIONS", "description": "List all organizations"},
        {"name": "SUPABASE_GETS_INFORMATION_ABOUT_THE_ORGANIZATION", "description": "Get organization information"},
        {"name": "SUPABASE_LIST_MEMBERS_OF_AN_ORGANIZATION", "description": "List organization members"},
        
        # Storage (Essential)
        {"name": "SUPABASE_LISTS_ALL_BUCKETS", "description": "List all storage buckets"},
        
        # Database Branches (Essential)
        {"name": "SUPABASE_CREATE_A_DATABASE_BRANCH", "description": "Create a database branch"},
        {"name": "SUPABASE_LIST_ALL_DATABASE_BRANCHES", "description": "List all database branches"},
        {"name": "SUPABASE_DELETE_A_DATABASE_BRANCH", "description": "Delete a database branch"},
        
        # API Keys (Essential)
        {"name": "SUPABASE_GET_PROJECT_API_KEYS", "description": "Get project API keys"},
        {"name": "SUPABASE_ALPHA_CREATES_A_NEW_API_KEY_FOR_THE_PROJECT", "description": "Create a new API key"},
        
        # Backups (Essential)
        {"name": "SUPABASE_LISTS_ALL_BACKUPS", "description": "List all backups"},
        {"name": "SUPABASE_RESTORES_A_PITR_BACKUP_FOR_A_DATABASE", "description": "Restore a PITR backup"},
        
        # Auth & SSO (Essential)
        {"name": "SUPABASE_BETA_AUTHORIZE_USER_THROUGH_OAUTH", "description": "Authorize user through OAuth"},
        {"name": "SUPABASE_GETS_PROJECT_S_AUTH_CONFIG", "description": "Get project auth configuration"},
    ],
    
    # ================== SOCIAL MEDIA ==================
    
    "linkedin": [
        # Posts (Essential)
        {"name": "LINKEDIN_CREATE_LINKED_IN_POST", "description": "Create a LinkedIn post"},
        {"name": "LINKEDIN_DELETE_LINKED_IN_POST", "description": "Delete a LinkedIn post"},
        
        # Profile & Company (Essential)
        {"name": "LINKEDIN_GET_MY_INFO", "description": "Get my profile information"},
        {"name": "LINKEDIN_GET_COMPANY_INFO", "description": "Get company information"},
    ],
    
    "facebook": [
        # Posts (Essential)
        {"name": "FACEBOOK_CREATE_POST", "description": "Create a post on page"},
        {"name": "FACEBOOK_CREATE_PHOTO_POST", "description": "Create a photo post"},
        {"name": "FACEBOOK_CREATE_VIDEO_POST", "description": "Create a video post"},
        {"name": "FACEBOOK_GET_POST", "description": "Get specific post"},
        {"name": "FACEBOOK_GET_PAGE_POSTS", "description": "Get page posts"},
        {"name": "FACEBOOK_UPDATE_POST", "description": "Update a post"},
        {"name": "FACEBOOK_DELETE_POST", "description": "Delete a post"},
        {"name": "FACEBOOK_GET_POST_INSIGHTS", "description": "Get post analytics"},
        {"name": "FACEBOOK_GET_POST_REACTIONS", "description": "Get post reactions"},
        {"name": "FACEBOOK_GET_SCHEDULED_POSTS", "description": "Get scheduled posts"},
        {"name": "FACEBOOK_PUBLISH_SCHEDULED_POST", "description": "Publish scheduled post"},
        {"name": "FACEBOOK_RESCHEDULE_POST", "description": "Reschedule a post"},
        
        # Media (Essential)
        {"name": "FACEBOOK_UPLOAD_PHOTO", "description": "Upload a photo"},
        {"name": "FACEBOOK_UPLOAD_PHOTOS_BATCH", "description": "Upload multiple photos"},
        {"name": "FACEBOOK_UPLOAD_VIDEO", "description": "Upload a video"},
        {"name": "FACEBOOK_CREATE_PHOTO_ALBUM", "description": "Create photo album"},
        {"name": "FACEBOOK_ADD_PHOTOS_TO_ALBUM", "description": "Add photos to album"},
        {"name": "FACEBOOK_GET_PAGE_PHOTOS", "description": "Get page photos"},
        {"name": "FACEBOOK_GET_PAGE_VIDEOS", "description": "Get page videos"},
        
        # Page Management (Essential)
        {"name": "FACEBOOK_GET_PAGE_DETAILS", "description": "Get page details"},
        {"name": "FACEBOOK_GET_PAGE_INSIGHTS", "description": "Get page analytics"},
        {"name": "FACEBOOK_GET_USER_PAGES", "description": "Get user's pages"},
        {"name": "FACEBOOK_LIST_MANAGED_PAGES", "description": "List managed pages"},
        {"name": "FACEBOOK_UPDATE_PAGE_SETTINGS", "description": "Update page settings"},
        {"name": "FACEBOOK_SEARCH_PAGES", "description": "Search for pages"},
        {"name": "FACEBOOK_GET_PAGE_ROLES", "description": "Get page roles"},
        
        # Comments & Reactions (Essential)
        {"name": "FACEBOOK_CREATE_COMMENT", "description": "Create comment on post"},
        {"name": "FACEBOOK_GET_COMMENTS", "description": "Get post comments"},
        {"name": "FACEBOOK_GET_COMMENT", "description": "Get specific comment"},
        {"name": "FACEBOOK_UPDATE_COMMENT", "description": "Update comment"},
        {"name": "FACEBOOK_DELETE_COMMENT", "description": "Delete a comment"},
        {"name": "FACEBOOK_LIKE_POST_OR_COMMENT", "description": "Like a post or comment"},
        {"name": "FACEBOOK_UNLIKE_POST_OR_COMMENT", "description": "Unlike a post or comment"},
        {"name": "FACEBOOK_ADD_REACTION", "description": "Add reaction to post"},
        
        # Messenger (Essential)
        {"name": "FACEBOOK_SEND_MESSAGE", "description": "Send message via Messenger"},
        {"name": "FACEBOOK_SEND_MEDIA_MESSAGE", "description": "Send media message"},
        {"name": "FACEBOOK_GET_PAGE_CONVERSATIONS", "description": "Get page conversations"},
        {"name": "FACEBOOK_GET_CONVERSATION_MESSAGES", "description": "Get conversation messages"},
        {"name": "FACEBOOK_GET_MESSAGE_DETAILS", "description": "Get message details"},
        {"name": "FACEBOOK_MARK_MESSAGE_SEEN", "description": "Mark message as seen"},
        
        # User (Essential)
        {"name": "FACEBOOK_GET_CURRENT_USER", "description": "Get current user information"},
    ],
    
    # ================== PAYMENT & FINANCE ==================
    
    "stripe": [
        # Customers (Essential)
        {"name": "STRIPE_CREATE_CUSTOMER", "description": "Create a new customer"},
        {"name": "STRIPE_RETRIEVE_CUSTOMER", "description": "Get customer details"},
        {"name": "STRIPE_UPDATE_CUSTOMER", "description": "Update customer"},
        {"name": "STRIPE_DELETE_CUSTOMER", "description": "Delete customer"},
        {"name": "STRIPE_LIST_CUSTOMERS", "description": "List all customers"},
        {"name": "STRIPE_SEARCH_CUSTOMERS", "description": "Search for customers"},
        
        # Payment Intents (Essential)
        {"name": "STRIPE_CREATE_PAYMENT_INTENT", "description": "Create payment intent"},
        {"name": "STRIPE_CONFIRM_PAYMENT_INTENT", "description": "Confirm payment intent"},
        {"name": "STRIPE_RETRIEVE_PAYMENT_INTENT", "description": "Get payment intent details"},
        {"name": "STRIPE_UPDATE_PAYMENT_INTENT", "description": "Update payment intent"},
        {"name": "STRIPE_LIST_PAYMENT_INTENTS", "description": "List payment intents"},
        
        # Charges & Refunds (Essential)
        {"name": "STRIPE_RETRIEVE_CHARGE", "description": "Get charge details"},
        {"name": "STRIPE_LIST_CHARGES", "description": "List charges"},
        {"name": "STRIPE_CREATE_REFUND", "description": "Create refund"},
        {"name": "STRIPE_RETRIEVE_REFUND", "description": "Get refund details"},
        {"name": "STRIPE_LIST_REFUNDS", "description": "List refunds"},
        
        # Subscriptions (Essential)
        {"name": "STRIPE_CREATE_SUBSCRIPTION", "description": "Create a subscription"},
        {"name": "STRIPE_RETRIEVE_SUBSCRIPTION", "description": "Get subscription details"},
        {"name": "STRIPE_UPDATE_SUBSCRIPTION", "description": "Update subscription"},
        {"name": "STRIPE_CANCEL_SUBSCRIPTION", "description": "Cancel a subscription"},
        {"name": "STRIPE_LIST_SUBSCRIPTIONS", "description": "List subscriptions"},
        
        # Products & Prices (Essential)
        {"name": "STRIPE_CREATE_PRODUCT", "description": "Create a product"},
        {"name": "STRIPE_LIST_PRODUCTS", "description": "List products"},
        {"name": "STRIPE_CREATE_PRICE", "description": "Create a price"},
        {"name": "STRIPE_LIST_PRICES", "description": "List prices"},
        
        # Invoices (Essential)
        {"name": "STRIPE_CREATE_INVOICE", "description": "Create invoice"},
        {"name": "STRIPE_LIST_INVOICES", "description": "List customer invoices"},
        
        # Checkout & Payment Links (Essential)
        {"name": "STRIPE_CREATE_CHECKOUT_SESSION", "description": "Create checkout session"},
        {"name": "STRIPE_LIST_PAYMENT_LINKS", "description": "List payment links"},
        
        # Payment Methods (Essential)
        {"name": "STRIPE_LIST_CUSTOMER_PAYMENT_METHODS", "description": "List customer payment methods"},
        
        # Balance (Essential)
        {"name": "STRIPE_RETRIEVE_BALANCE", "description": "Get account balance"},
        
        # Tax (Essential)
        {"name": "STRIPE_LIST_TAX_CODES", "description": "List tax codes"},
        {"name": "STRIPE_LIST_TAX_RATES", "description": "List tax rates"},
        
        # Shipping & Coupons (Essential)
        {"name": "STRIPE_LIST_SHIPPING_RATES", "description": "List shipping rates"},
        {"name": "STRIPE_LIST_COUPONS", "description": "List coupons"},
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
