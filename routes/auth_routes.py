"""Authentication routes."""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from auth import get_authorization_url, handle_oauth_callback

router = APIRouter()


@router.get("/auth/google")
async def auth_google():
    """Initiate Google OAuth flow."""
    try:
        authorization_url = get_authorization_url()
        return RedirectResponse(url=authorization_url)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle Google OAuth callback."""
    code = request.query_params.get("code")
    try:
        email = handle_oauth_callback(code)
        return RedirectResponse(url="/")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

