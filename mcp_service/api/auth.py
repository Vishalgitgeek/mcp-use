"""API authentication utilities."""
import os
from fastapi import Header, HTTPException


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
    # Read dynamically to support testing
    agent_api_key = os.getenv("AGENT_API_KEY", "")

    if not agent_api_key:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: AGENT_API_KEY not set"
        )

    if x_api_key != agent_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return x_api_key
