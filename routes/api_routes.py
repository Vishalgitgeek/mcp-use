"""API routes for accounts and execution."""
from fastapi import APIRouter, Request, HTTPException
from token_manager import get_connected_accounts
from services.agent_service import execute_agent_query

router = APIRouter()


@router.get("/api/accounts")
async def get_accounts():
    """Get list of connected accounts."""
    return get_connected_accounts()


@router.post("/api/execute")
async def execute_query(request: Request):
    """Execute a query using MCPAgent with selected account."""
    data = await request.json()
    email = data.get("email")
    query = data.get("query")
    
    if not email or not query:
        raise HTTPException(status_code=400, detail="Email and query are required")
    
    try:
        result = await execute_agent_query(email, query)
        return {"result": str(result)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

