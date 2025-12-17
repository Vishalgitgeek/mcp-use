"""Integration API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from typing import Optional

from ..models.integration import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationListResponse,
    ConnectResponse
)
from ..services.integration_service import get_integration_service
from ..config import SUPPORTED_INTEGRATIONS, OAUTH_REDIRECT_BASE
from .auth import verify_user_token

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.get("", response_model=list[str])
async def list_available_integrations():
    """
    List all available integrations.

    Returns list of supported integration provider names.
    """
    return SUPPORTED_INTEGRATIONS


@router.get("/connected", response_model=IntegrationListResponse)
async def list_connected_integrations(user_id: str = Depends(verify_user_token)):
    """
    List user's connected integrations.

    Requires user authentication.
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
    user_id: str = Depends(verify_user_token)
):
    """
    Initiate OAuth connection for an integration.

    Returns an auth_url that the user should be redirected to.
    """
    provider = request.provider.lower()

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
    error_description: Optional[str] = None
):
    """
    OAuth callback endpoint.

    Composio will redirect here after user completes OAuth.
    """
    if error:
        # OAuth error
        return RedirectResponse(
            url=f"{OAUTH_REDIRECT_BASE}/?error={error}"
        )

    # Composio sends: status=success&connectedAccountId=xxx&appName=gmail
    if status == "success" and appName:
        return RedirectResponse(
            url=f"{OAUTH_REDIRECT_BASE}/?connected={appName}"
        )

    # Fallback - redirect to home
    return RedirectResponse(url=f"{OAUTH_REDIRECT_BASE}/")


@router.post("/callback/complete")
async def complete_connection(
    provider: str,
    connected_email: Optional[str] = None,
    user_id: str = Depends(verify_user_token)
):
    """
    Manually complete a connection after OAuth callback.

    Called by frontend after OAuth redirect to update status.
    """
    service = get_integration_service()

    try:
        result = await service.complete_connection(
            user_id=user_id,
            provider=provider,
            connected_email=connected_email
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/connections")
async def debug_list_all_connections(user_id: str = Depends(verify_user_token)):
    """
    Debug endpoint: List all raw Composio connections for user.
    """
    from ..services.composio_service import get_composio_service

    composio = get_composio_service()

    try:
        connections = composio.client.connected_accounts.list(user_ids=user_id)
        result = []
        for conn in connections.items:
            # Capture all attributes
            conn_data = {
                "id": conn.id,
                "attributes": dir(conn),
            }
            # Try to get common attributes
            for attr in ['toolkit', 'appName', 'app_name', 'authConfigId', 'auth_config_id',
                        'integrationId', 'integration_id', 'status', 'connectionParams']:
                conn_data[attr] = getattr(conn, attr, None)
                # If it's an object, try to get its dict
                if hasattr(conn_data[attr], '__dict__'):
                    conn_data[attr] = str(conn_data[attr].__dict__)

            result.append(conn_data)

        return {"user_id": user_id, "connections": result, "count": len(result)}

    except Exception as e:
        return {"error": str(e)}


@router.delete("/{provider}")
async def disconnect_integration(
    provider: str,
    user_id: str = Depends(verify_user_token)
):
    """
    Disconnect an integration.
    """
    service = get_integration_service()

    success = await service.disconnect(user_id, provider)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No {provider} integration found for user"
        )

    return {"message": f"{provider} disconnected successfully"}


@router.get("/{provider}/status")
async def get_integration_status(
    provider: str,
    user_id: str = Depends(verify_user_token)
):
    """
    Get status of a specific integration.
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
