"""Integration API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from ..models.integration import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationListResponse,
    ConnectResponse,
    DisconnectRequest
)
from ..services.integration_service import get_integration_service
from ..config import SUPPORTED_INTEGRATIONS, OAUTH_REDIRECT_BASE
from ..tools_config import TOOL_METADATA
from .auth import verify_api_key

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("")
async def list_available_integrations(
    detailed: bool = True,
    _: str = Depends(verify_api_key)
):
    """
    List all available integrations.

    Requires X-API-Key header.

    Args:
        detailed: If True (default), returns full details with descriptions.
                  If False, returns simple list of provider names.

    Returns:
        List of integrations with name, description, and category (or simple list)
    """
    if not detailed:
        return SUPPORTED_INTEGRATIONS

    # Helper to generate display name from provider key
    def get_display_name(provider: str) -> str:
        # Handle special cases like "googledocs" -> "Google Docs"
        name_map = {
            "gmail": "Gmail",
            "slack": "Slack",
            "whatsapp": "WhatsApp",
            "googledocs": "Google Docs",
            "googlesheets": "Google Sheets",
            "googledrive": "Google Drive",
            "googlebigquery": "Google BigQuery",
            "googlemeet": "Google Meet",
            "googleads": "Google Ads",
            "googlemaps": "Google Maps",
            "zoom": "Zoom",
            "youtube": "YouTube",
            "supabase": "Supabase",
            "linkedin": "LinkedIn",
            "facebook": "Facebook",
            "stripe": "Stripe",
        }
        return name_map.get(provider, provider.title())

    return {
        "integrations": [
            {
                "provider": provider,
                "name": get_display_name(provider),
                "description": TOOL_METADATA.get(provider, {}).get("description", ""),
                "category": TOOL_METADATA.get(provider, {}).get("category", "").title()
            }
            for provider in SUPPORTED_INTEGRATIONS
        ],
        "total": len(SUPPORTED_INTEGRATIONS)
    }


@router.get("/connected", response_model=IntegrationListResponse)
async def list_connected_integrations(
    user_id: str = Query(..., description="User ID to get integrations for"),
    _: str = Depends(verify_api_key)
):
    """
    List user's connected integrations.

    Requires X-API-Key header and user_id query parameter.
    """
    service = get_integration_service()
    integrations = await service.get_user_integrations(user_id)

    return IntegrationListResponse(
        integrations=[
            IntegrationResponse(
                provider=i["provider"],
                status=i["status"],
                connected_email=i.get("connected_email"),
                connected_at=i.get("connected_at")
            )
            for i in integrations
        ]
    )


@router.post("/connect", response_model=ConnectResponse)
async def initiate_connection(
    request: IntegrationCreate,
    _: str = Depends(verify_api_key)
):
    """
    Initiate OAuth connection for an integration.

    Requires X-API-Key header.
    Returns an auth_url that the user should be redirected to.
    """
    provider = request.provider.lower()
    user_id = request.user_id

    if provider not in SUPPORTED_INTEGRATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported integration: {provider}. Supported: {SUPPORTED_INTEGRATIONS}"
        )

    service = get_integration_service()

    try:
        result = await service.initiate_connection(
            user_id,
            provider,
            redirect_url=request.redirect_url,
            force_reauth=request.force_reauth
        )

        # Handle already_connected case
        if result.get("status") == "already_connected":
            return ConnectResponse(
                auth_url=None,
                status="already_connected",
                message=f"{provider} is already connected"
            )

        return ConnectResponse(
            auth_url=result["auth_url"],
            message=f"Redirect user to auth_url to connect {provider}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


@router.get("/callback")
async def oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[str] = None,
    connectedAccountId: Optional[str] = None,
    appName: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    session_id: Optional[str] = None

):
    """
    OAuth callback endpoint.

    Composio will redirect here after user completes OAuth.
    No API key required - this is called by Composio/OAuth provider.
    """
    import logging
    from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
    from ..services.integration_service import get_oauth_session

    logger = logging.getLogger("mcp.oauth")

    logger.info(f"OAuth callback received: status={status}, appName={appName}, "
                f"connectedAccountId={connectedAccountId}, session_id={session_id}")

    service = get_integration_service()

    # ============================================================
    # Session-based redirect URL lookup (PRIMARY METHOD)
    # ============================================================
    # The session_id is passed in the callback URL we gave to Composio
    # It maps to the user's desired redirect_url stored in MongoDB
    # ============================================================

    final_redirect = None

    # Primary method: Look up by session_id
    if session_id:
        session = await get_oauth_session(session_id)
        if session:
            final_redirect = session.get("redirect_url")
            logger.info(f"Retrieved redirect_url from session {session_id}: {final_redirect}")
        else:
            logger.warning(f"Session {session_id} not found - may have expired")

    # Fallback: Use default redirect
    if not final_redirect:
        final_redirect = OAUTH_REDIRECT_BASE
        logger.info(f"No session redirect found, using default: {final_redirect}")

    # Ensure redirect URL has a proper protocol (https:// or http://)
    # Without protocol, browser treats it as a relative path
    if final_redirect and not final_redirect.startswith(('http://', 'https://')):
        final_redirect = f"https://{final_redirect}"
        logger.info(f"Added https:// to redirect URL: {final_redirect}")

    # Helper function to append query params to URL properly
    def append_params(url: str, params: dict) -> str:
        """Append query parameters to URL, handling existing params correctly."""
        parsed = urlparse(url)
        existing_params = parse_qs(parsed.query)
        # Flatten single-value lists from parse_qs
        existing_params = {k: v[0] if len(v) == 1 else v for k, v in existing_params.items()}
        existing_params.update(params)
        new_query = urlencode(existing_params)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                          parsed.params, new_query, parsed.fragment))

    if error:
        # OAuth error
        error_msg = error_description or error
        redirect_with_error = append_params(final_redirect, {
            "error": error,
            "message": error_msg
        })
        logger.info(f"OAuth error, redirecting to: {redirect_with_error}")
        return RedirectResponse(url=redirect_with_error)

    # Composio sends: status=success&connectedAccountId=xxx&appName=gmail
    if status == "success" and appName:
        # Mark integration as active
        if connectedAccountId:
            integration = await service.get_integration_by_connection_id(connectedAccountId)
            if integration:
                await service.complete_connection(
                    user_id=integration["user_id"],
                    provider=appName
                )

        redirect_with_success = append_params(final_redirect, {
            "status": "success",
            "appName": appName
        })
        logger.info(f"OAuth success, redirecting to: {redirect_with_success}")
        return RedirectResponse(url=redirect_with_success)

    # Fallback - redirect with status
    redirect_with_status = append_params(final_redirect, {"status": "callback_received"})
    logger.info(f"OAuth callback fallback, redirecting to: {redirect_with_status}")
    return RedirectResponse(url=redirect_with_status)


@router.post("/disconnect")
async def disconnect_integration(
    request: DisconnectRequest,
    _: str = Depends(verify_api_key)
):
    """
    Disconnect an integration.

    Requires X-API-Key header.
    """
    service = get_integration_service()

    success = await service.disconnect(request.user_id, request.provider)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No {request.provider} integration found for user"
        )

    return {"message": f"{request.provider} disconnected successfully"}


@router.get("/{provider}/status")
async def get_integration_status(
    provider: str,
    user_id: str = Query(..., description="User ID to check status for"),
    _: str = Depends(verify_api_key)
):
    """
    Get status of a specific integration.

    Requires X-API-Key header and user_id query parameter.
    """
    service = get_integration_service()
    integration = await service.get_integration(user_id, provider)

    if not integration:
        return {"provider": provider, "status": "not_connected"}

    return {
        "provider": provider,
        "status": integration.get("status"),
        "connected_email": integration.get("connected_email")
    }
