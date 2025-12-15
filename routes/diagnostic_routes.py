"""Diagnostic routes for troubleshooting OAuth setup."""
from fastapi import APIRouter, HTTPException
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

router = APIRouter()


@router.get("/api/diagnostic/oauth")
async def diagnostic_oauth():
    """Check OAuth configuration status."""
    issues = []
    warnings = []
    
    # Check Client ID
    if not GOOGLE_CLIENT_ID:
        issues.append("GOOGLE_CLIENT_ID is not set in .env file")
    elif not GOOGLE_CLIENT_ID.endswith(".apps.googleusercontent.com"):
        warnings.append("GOOGLE_CLIENT_ID format looks incorrect (should end with .apps.googleusercontent.com)")
    
    # Check Client Secret
    if not GOOGLE_CLIENT_SECRET:
        issues.append("GOOGLE_CLIENT_SECRET is not set in .env file")
    elif len(GOOGLE_CLIENT_SECRET) < 20:
        warnings.append("GOOGLE_CLIENT_SECRET seems too short (might be incorrect)")
    
    # Check Redirect URI
    if not GOOGLE_REDIRECT_URI:
        issues.append("GOOGLE_REDIRECT_URI is not set")
    elif "localhost" not in GOOGLE_REDIRECT_URI and "127.0.0.1" not in GOOGLE_REDIRECT_URI:
        warnings.append("Redirect URI should include localhost or 127.0.0.1 for local development")
    
    status = "ok" if not issues else "error"
    
    return {
        "status": status,
        "config": {
            "client_id_set": bool(GOOGLE_CLIENT_ID),
            "client_id_preview": GOOGLE_CLIENT_ID[:30] + "..." if GOOGLE_CLIENT_ID and len(GOOGLE_CLIENT_ID) > 30 else GOOGLE_CLIENT_ID,
            "client_secret_set": bool(GOOGLE_CLIENT_SECRET),
            "redirect_uri": GOOGLE_REDIRECT_URI
        },
        "issues": issues,
        "warnings": warnings,
        "next_steps": [
            "1. Create a Google Cloud project at https://console.cloud.google.com/",
            "2. Enable Google Drive API",
            "3. Configure OAuth consent screen",
            "4. Create OAuth 2.0 Client ID (Web application)",
            "5. Add redirect URI: http://localhost:8000/auth/callback",
            "6. Copy Client ID and Secret to .env file",
            "7. See OAUTH_SETUP.md for detailed instructions"
        ] if issues else []
    }

