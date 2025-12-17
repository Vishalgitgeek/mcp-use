"""Google OAuth authentication endpoints."""
import os
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow

from ..config import OAUTH_REDIRECT_BASE

router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 1 week

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# OAuth scopes
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]


def get_google_flow() -> Flow:
    """Create Google OAuth flow."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )

    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [f"{OAUTH_REDIRECT_BASE}/api/auth/google/callback"]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=f"{OAUTH_REDIRECT_BASE}/api/auth/google/callback"
    )
    return flow


def create_jwt_token(user_id: str, email: str) -> str:
    """Create JWT token for user."""
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/google")
async def google_login():
    """Redirect to Google OAuth."""
    flow = get_google_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(code: str = None, error: str = None):
    """Handle Google OAuth callback."""
    if error:
        return RedirectResponse(url=f"/?error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="No authorization code")

    try:
        flow = get_google_flow()
        flow.fetch_token(code=code)

        credentials = flow.credentials

        # Verify the ID token
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Extract user info
        user_id = id_info.get("sub")
        email = id_info.get("email")

        if not user_id or not email:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        # Create JWT token
        token = create_jwt_token(user_id, email)

        # Redirect to frontend with token
        return RedirectResponse(url=f"/?token={token}")

    except Exception as e:
        return RedirectResponse(url=f"/?error={str(e)}")


@router.get("/me")
async def get_current_user(request: Request):
    """Get current user info from JWT token."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header[7:]
    payload = decode_jwt_token(token)

    return {
        "id": payload.get("sub"),
        "email": payload.get("email")
    }
