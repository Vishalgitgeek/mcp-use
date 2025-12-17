"""API authentication utilities."""
from fastapi import Header, HTTPException, Depends
from typing import Optional

from ..config import AGENT_API_KEY


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """
    Verify API key for agent authentication.

    Args:
        x_api_key: API key from request header

    Returns:
        The verified API key

    Raises:
        HTTPException: If API key is invalid
    """
    if not AGENT_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: AGENT_API_KEY not set"
        )

    if x_api_key != AGENT_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return x_api_key


async def verify_user_token(authorization: str = Header(...)) -> str:
    """
    Verify user JWT token and extract user_id.

    Args:
        authorization: Bearer token from request header

    Returns:
        User ID extracted from token

    Raises:
        HTTPException: If token is invalid
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )

    token = authorization[7:]  # Remove "Bearer " prefix

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # Decode JWT token
    from .google_auth import decode_jwt_token
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: no user ID"
        )

    return user_id


def get_user_id_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Optional user ID extraction from header.

    Args:
        authorization: Optional Bearer token

    Returns:
        User ID or None
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    return authorization[7:]
