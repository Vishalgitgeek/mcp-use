"""Tools API endpoints for AI agent integration."""
from fastapi import APIRouter, HTTPException, Depends

from ..models.integration import (
    ToolExecuteRequest,
    ToolExecuteResponse,
    ToolListResponse,
    ToolInfo
)
from ..services.integration_service import get_integration_service
from .auth import verify_api_key

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("", response_model=ToolListResponse)
async def list_user_tools(
    user_id: str,
    _: str = Depends(verify_api_key)
):
    """
    List available tools for a user.

    This endpoint is called by the AI agent to discover what tools
    are available for a specific user based on their connected integrations.

    Args:
        user_id: The user ID to get tools for

    Returns:
        List of available tools with their definitions
    """
    service = get_integration_service()

    try:
        tools = await service.get_user_tools(user_id)

        return ToolListResponse(
            tools=[
                ToolInfo(
                    name=t["name"],
                    description=t.get("description", ""),
                    provider=t.get("provider", ""),
                    parameters=t.get("parameters", {})
                )
                for t in tools
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {str(e)}")


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    _: str = Depends(verify_api_key)
):
    """
    Execute a tool/action for a user.

    This is the main endpoint called by the AI agent to execute
    actions on behalf of users.

    Args:
        request: Tool execution request containing:
            - user_id: The user to execute the action for
            - action: The action to execute (e.g., 'GMAIL_SEND_EMAIL')
            - params: Parameters for the action

    Returns:
        Execution result
    """
    service = get_integration_service()

    try:
        result = await service.execute_tool(
            user_id=request.user_id,
            action=request.action,
            params=request.params
        )

        return ToolExecuteResponse(
            success=result.get("success", False),
            result=result.get("result"),
            error=result.get("error")
        )

    except Exception as e:
        return ToolExecuteResponse(
            success=False,
            error=f"Execution failed: {str(e)}"
        )


@router.get("/actions/{provider}")
async def list_provider_actions(
    provider: str,
    include_schema: bool = True,
    _: str = Depends(verify_api_key)
):
    """
    List available actions for a specific provider with full schemas.

    Fetches actions from actions_config.py and enriches them with
    parameter schemas from Composio API.

    Args:
        provider: Integration provider (e.g., 'gmail', 'slack')
        include_schema: Whether to include request/response schemas (default: True)

    Returns:
        List of available actions with their schemas
    """
    from ..actions_config import get_provider_actions, is_provider_supported
    import requests
    import os
    
    provider_lower = provider.lower()
    
    # Check if provider is supported
    if not is_provider_supported(provider_lower):
        raise HTTPException(
            status_code=404,
            detail=f"Unknown provider: {provider}. No actions defined for this provider."
        )
    
    try:
        # Get actions from config
        actions = get_provider_actions(provider_lower)
        
        # If schema is not requested, return basic actions
        if not include_schema:
            return {
                "provider": provider_lower,
                "actions": actions,
                "schema_included": False,
                "total_actions": len(actions)
            }
        
        # Fetch schemas from Composio API
        composio_api_key = os.getenv("COMPOSIO_API_KEY")
        if not composio_api_key:
            # If no Composio key, return without schemas
            return {
                "provider": provider_lower,
                "actions": actions,
                "schema_included": False,
                "total_actions": len(actions),
                "note": "COMPOSIO_API_KEY not configured - schemas unavailable"
            }
        
        # Fetch all action schemas from Composio
        composio_url = "https://backend.composio.dev/api/v2/actions"
        headers = {"X-API-Key": composio_api_key}
        params = {"apps": provider_lower}
        
        try:
            response = requests.get(composio_url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                composio_data = response.json()
                # Create lookup map by action name
                composio_actions = {
                    item["name"]: item 
                    for item in composio_data.get("items", [])
                }
                
                # Enrich actions with schemas
                enriched_actions = []
                for action in actions:
                    action_name = action["name"]
                    enriched = {
                        "name": action_name,
                        "description": action["description"]
                    }
                    
                    # Add schema if available
                    if action_name in composio_actions:
                        composio_action = composio_actions[action_name]
                        
                        # Request schema
                        if "parameters" in composio_action:
                            params_data = composio_action["parameters"]
                            enriched["request_schema"] = {
                                "type": params_data.get("type", "object"),
                                "properties": params_data.get("properties", {}),
                                "required": params_data.get("required", [])
                            }
                        
                        # Response schema
                        if "response" in composio_action:
                            response_data = composio_action["response"]
                            enriched["response_schema"] = {
                                "type": response_data.get("type", "object"),
                                "properties": response_data.get("properties", {})
                            }
                    
                    enriched_actions.append(enriched)
                
                return {
                    "provider": provider_lower,
                    "actions": enriched_actions,
                    "schema_included": True,
                    "total_actions": len(enriched_actions)
                }
                
        except requests.RequestException as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch schemas from Composio: {e}")
            
            # Fallback to basic actions
            return {
                "provider": provider_lower,
                "actions": actions,
                "schema_included": False,
                "total_actions": len(actions),
                "error": f"Failed to fetch schemas: {str(e)}"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get actions for {provider}: {str(e)}"
        )


@router.get("/schema/{action}")
async def get_action_schema(
    action: str,
    _: str = Depends(verify_api_key)
):
    """
    Get the parameter schema for a specific action from Composio.

    Args:
        action: Action name (e.g., 'GMAIL_SEND_EMAIL')

    Returns:
        Action schema with parameters from Composio
    """
    import requests
    import os

    # Extract provider from action name (e.g., GMAIL_SEND_EMAIL -> gmail)
    provider = action.split("_")[0].lower()

    try:
        composio_api_key = os.getenv("COMPOSIO_API_KEY")
        if not composio_api_key:
            raise HTTPException(
                status_code=500,
                detail="COMPOSIO_API_KEY not configured"
            )

        # Fetch action schema directly from Composio API
        composio_url = "https://backend.composio.dev/api/v2/actions"
        headers = {"X-API-Key": composio_api_key}
        params = {"apps": provider}

        response = requests.get(composio_url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Composio API error: {response.status_code}"
            )

        composio_data = response.json()
        actions = composio_data.get("items", [])

        # Find the specific action
        for item in actions:
            if item.get("name") == action:
                result = {
                    "action": action,
                    "description": item.get("description", ""),
                }

                # Include request parameters schema
                if "parameters" in item:
                    params_data = item["parameters"]
                    result["parameters"] = {
                        "type": params_data.get("type", "object"),
                        "properties": params_data.get("properties", {}),
                        "required": params_data.get("required", [])
                    }

                # Include response schema if available
                if "response" in item:
                    result["response_schema"] = item["response"]

                return result

        raise HTTPException(status_code=404, detail=f"Action not found: {action}")

    except HTTPException:
        raise
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to reach Composio API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch schema: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Can be called without authentication to verify service is running.
    """
    return {"status": "healthy", "service": "mcp-integration-service"}
