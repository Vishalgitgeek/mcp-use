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
from .auth import verify_api_key

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("", response_model=list[str])
async def list_available_integrations(
    _: str = Depends(verify_api_key)
):
    """
    List all available integrations.

    Requires X-API-Key header.
    Returns list of supported integration provider names.
    """
    return SUPPORTED_INTEGRATIONS


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
    redirect_url: Optional[str] = None,
    entity_id: Optional[str] = None
):
    """
    OAuth callback endpoint.

    Composio will redirect here after user completes OAuth.
    No API key required - this is called by Composio/OAuth provider.
    """
    # Determine where to redirect after callback
    final_redirect = redirect_url or OAUTH_REDIRECT_BASE

    if error:
        # OAuth error
        return RedirectResponse(
            url=f"{final_redirect}?error={error}"
        )

    # Composio sends: status=success&connectedAccountId=xxx&appName=gmail&entity_id=user_xxx
    if status == "success" and appName:
        # Extract user_id from entity_id (entity_id is "user_{user_id}")
        if entity_id and entity_id.startswith("user_"):
            user_id = entity_id.replace("user_", "")
            provider = appName.lower()
            
            # Update MongoDB to mark integration as active
            try:
                service = get_integration_service()
                await service.complete_connection(user_id, provider)
            except Exception as e:
                # Log error but don't fail the redirect
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error completing connection in MongoDB: {e}")
        
        return RedirectResponse(
            url=f"{final_redirect}?connected={appName}&status=success"
        )

    # Fallback - redirect with status
    return RedirectResponse(url=f"{final_redirect}?status=callback_received")


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
