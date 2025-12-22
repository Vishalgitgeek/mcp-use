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
    _: str = Depends(verify_api_key)
):
    """
    List available actions for a specific provider.

    Useful for the AI agent to know what actions are available
    for a specific integration type.

    Args:
        provider: Integration provider (e.g., 'gmail', 'slack')

    Returns:
        List of available actions for the provider
    """
    # Common actions for supported providers (using actual Composio action names)
    provider_actions = {
        "gmail": [
            {"name": "GMAIL_SEND_EMAIL", "description": "Send an email"},
            {"name": "GMAIL_FETCH_EMAILS", "description": "Fetch/search emails with optional query filter"},
            {"name": "GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID", "description": "Get a specific email by message ID"},
            {"name": "GMAIL_FETCH_MESSAGE_BY_THREAD_ID", "description": "Get all messages in a thread"},
            {"name": "GMAIL_CREATE_EMAIL_DRAFT", "description": "Create an email draft"},
            {"name": "GMAIL_ADD_LABEL_TO_EMAIL", "description": "Add or remove labels from an email"},
            {"name": "GMAIL_LIST_LABELS", "description": "List all Gmail labels"},
            {"name": "GMAIL_DELETE_MESSAGE", "description": "Permanently delete an email"},
        ],
        "slack": [
            {"name": "SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL", "description": "Send a message to a channel"},
            {"name": "SLACK_LIST_ALL_SLACK_TEAM_CHANNELS_WITH_PAGINATION", "description": "List available channels"},
            {"name": "SLACK_FETCHES_CONVERSATION_HISTORY", "description": "Get channel message history"},
            {"name": "SLACK_SEARCH_MESSAGES_IN_SLACK", "description": "Search for messages"},
        ]
    }

    provider_lower = provider.lower()
    if provider_lower not in provider_actions:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown provider: {provider}"
        )

    return {
        "provider": provider_lower,
        "actions": provider_actions[provider_lower]
    }


@router.get("/schema/{action}")
async def get_action_schema(
    action: str,
    user_id: str,
    _: str = Depends(verify_api_key)
):
    """
    Get the parameter schema for a specific action from Composio.

    Args:
        action: Action name (e.g., 'GMAIL_SEND_EMAIL')
        user_id: User ID to fetch schema for

    Returns:
        Action schema with parameters from Composio
    """
    from ..services.composio_service import get_composio_service

    provider = action.split("_")[0].lower()

    try:
        composio = get_composio_service()
        entity_id = f"user_{user_id}"
        tools = composio.client.tools.get(
            user_id=entity_id,
            toolkits=[provider.upper()]
        )

        for tool in tools:
            if getattr(tool, 'name', '') == action:
                return {
                    "action": action,
                    "description": getattr(tool, 'description', ''),
                    "parameters": getattr(tool, 'parameters', {})
                }

        raise HTTPException(status_code=404, detail=f"Action not found: {action}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch schema: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Can be called without authentication to verify service is running.
    """
    return {"status": "healthy", "service": "mcp-integration-service"}
