"""Integration models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class IntegrationStatus(str, Enum):
    """Status of an integration connection."""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"


class IntegrationCreate(BaseModel):
    """Request model for creating an integration connection."""
    provider: str = Field(..., description="Integration provider (e.g., gmail, slack)")


class Integration(BaseModel):
    """Integration document model for MongoDB."""
    user_id: str = Field(..., description="User ID from your auth system")
    provider: str = Field(..., description="Integration provider name")
    composio_entity_id: str = Field(..., description="Entity ID for Composio SDK")
    composio_connection_id: Optional[str] = Field(None, description="Connection ID from Composio")
    status: IntegrationStatus = Field(default=IntegrationStatus.PENDING)
    connected_email: Optional[str] = Field(None, description="Email of the connected account")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class IntegrationResponse(BaseModel):
    """Response model for integration data."""
    provider: str
    status: str
    connected_email: Optional[str] = None
    connected_at: Optional[datetime] = None


class IntegrationListResponse(BaseModel):
    """Response model for listing integrations."""
    integrations: list[IntegrationResponse]


class ConnectResponse(BaseModel):
    """Response model for connect request."""
    auth_url: str
    message: str = "Redirect user to auth_url to complete connection"


class ToolExecuteRequest(BaseModel):
    """Request model for tool execution."""
    user_id: str = Field(..., description="User ID to execute tool for")
    action: str = Field(..., description="Action to execute (e.g., GMAIL_SEND_EMAIL)")
    params: dict = Field(default_factory=dict, description="Parameters for the action")


class ToolExecuteResponse(BaseModel):
    """Response model for tool execution."""
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None


class ToolInfo(BaseModel):
    """Information about an available tool."""
    name: str
    description: str
    provider: str
    parameters: dict


class ToolListResponse(BaseModel):
    """Response model for listing available tools."""
    tools: list[ToolInfo]
