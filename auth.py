"""Google OAuth authentication handling."""
from typing import Tuple
from fastapi import HTTPException
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google.auth.transport.requests
import requests
from config import get_google_client_config, GOOGLE_REDIRECT_URI, GOOGLE_SCOPES
from token_manager import save_tokens, load_tokens


def create_oauth_flow() -> Flow:
    """Create a Google OAuth flow instance."""
    client_config = get_google_client_config()
    flow = Flow.from_client_config(
        client_config,
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    return flow


def get_authorization_url() -> str:
    """Get the Google OAuth authorization URL."""
    flow = create_oauth_flow()
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url


def handle_oauth_callback(code: str) -> str:
    """
    Handle OAuth callback and save tokens.
    
    Args:
        code: Authorization code from OAuth callback
        
    Returns:
        User email address
        
    Raises:
        HTTPException: If authentication fails
    """
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    flow = create_oauth_flow()
    
    # Fetch token - handle scope changes gracefully
    # Google automatically adds 'openid' scope when using userinfo scopes
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
    except Exception as e:
        error_str = str(e)
        # If error is about scope changes (Google added 'openid'), handle it manually
        if "Scope has changed" in error_str:
            # Manually exchange the authorization code for tokens
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'code': code,
                'client_id': flow.client_config['web']['client_id'],
                'client_secret': flow.client_config['web']['client_secret'],
                'redirect_uri': GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
            response = requests.post(token_url, data=token_data)
            if response.status_code == 200:
                token_info = response.json()
                # Create credentials manually with the scopes Google actually returned
                credentials = Credentials(
                    token=token_info['access_token'],
                    refresh_token=token_info.get('refresh_token'),
                    token_uri=token_url,
                    client_id=flow.client_config['web']['client_id'],
                    client_secret=flow.client_config['web']['client_secret'],
                    scopes=token_info.get('scope', '').split() if 'scope' in token_info else GOOGLE_SCOPES + ['openid']
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to exchange authorization code: {response.text}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"OAuth token exchange failed: {str(e)}"
            )
    
    # Get user email - try multiple methods
    email = None
    
    # Method 1: Try to get from userinfo API
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        email = user_info.get('email')
    except Exception as e:
        # Method 2: Try to extract from ID token if available
        if hasattr(credentials, 'id_token') and credentials.id_token:
            try:
                import base64
                import json
                # Decode JWT token (simple base64 decode for payload)
                parts = credentials.id_token.split('.')
                if len(parts) >= 2:
                    # Add padding if needed
                    payload = parts[1]
                    padding = len(payload) % 4
                    if padding:
                        payload += '=' * (4 - padding)
                    decoded = base64.urlsafe_b64decode(payload)
                    token_data = json.loads(decoded)
                    email = token_data.get('email')
            except Exception:
                pass
        
        # If still no email, raise error
        if not email:
            raise HTTPException(
                status_code=400,
                detail=f"Could not retrieve user email. Please ensure userinfo scopes are enabled. Error: {str(e)}"
            )
    
    if not email:
        raise HTTPException(
            status_code=400, 
            detail="Could not retrieve user email. Please re-authorize the application."
        )
    
    # Save tokens
    tokens = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }
    
    save_tokens(email, tokens)
    return email


def get_credentials_for_user(email: str) -> Credentials:
    """
    Get Google credentials for a user, refreshing if necessary.
    
    Args:
        email: User email address
        
    Returns:
        Google Credentials object
        
    Raises:
        ValueError: If tokens not found for user
    """
    tokens = load_tokens(email)
    if not tokens:
        raise ValueError(f"No tokens found for {email}")
    
    creds = Credentials(
        token=tokens["token"],
        refresh_token=tokens.get("refresh_token"),
        token_uri=tokens["token_uri"],
        client_id=tokens["client_id"],
        client_secret=tokens["client_secret"],
        scopes=tokens["scopes"]
    )
    
    # Refresh token if needed
    if creds.expired and creds.refresh_token:
        creds.refresh(google.auth.transport.requests.Request())
        # Save refreshed token
        tokens["token"] = creds.token
        save_tokens(email, tokens)
    
    return creds

