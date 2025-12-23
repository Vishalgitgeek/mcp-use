"""Database API endpoints for managing user database connections."""
from fastapi import APIRouter, HTTPException, Depends, Query

from ..models.database import (
    DatabaseType,
    DatabaseConnectRequest,
    DatabaseConnectResponse,
    DatabaseTestRequest,
    DatabaseTestResponse,
    DatabaseDisconnectRequest,
    DatabaseListResponse,
    DatabaseInfo,
    DatabaseSchema,
)
from ..services.database_service import get_database_service
from ..config import SUPPORTED_DATABASES
from .auth import verify_api_key

router = APIRouter(prefix="/api/databases", tags=["databases"])


@router.get("/types")
async def list_database_types(
    _: str = Depends(verify_api_key)
):
    """
    List all supported database types with their credential schemas.

    This endpoint returns the form schema for each database type,
    allowing the frontend to dynamically render connection forms.

    Requires X-API-Key header.
    """
    service = get_database_service()
    db_types = service.get_supported_databases()

    return {
        "databases": [
            {
                "type": db.type.value,
                "display_name": db.display_name,
                "description": db.description,
                "fields": [field.model_dump() for field in db.fields]
            }
            for db in db_types
        ]
    }


@router.post("/test", response_model=DatabaseTestResponse)
async def test_database_connection(
    request: DatabaseTestRequest,
    _: str = Depends(verify_api_key)
):
    """
    Test a database connection without saving it.

    Use this to validate credentials before connecting.

    Requires X-API-Key header.
    """
    if request.db_type.value not in SUPPORTED_DATABASES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported database type: {request.db_type}. Supported: {SUPPORTED_DATABASES}"
        )

    service = get_database_service()

    success, message, schema = await service.test_connection(
        request.db_type,
        request.credentials
    )

    return DatabaseTestResponse(
        success=success,
        message=message,
        schema=schema
    )


@router.post("/connect", response_model=DatabaseConnectResponse)
async def connect_database(
    request: DatabaseConnectRequest,
    _: str = Depends(verify_api_key)
):
    """
    Connect a database for a user.

    This will:
    1. Test the connection
    2. Fetch the database schema
    3. Encrypt and store credentials
    4. Return the schema

    If user already has a database of this type connected,
    it will be replaced with the new connection.

    Requires X-API-Key header.
    """
    if request.db_type.value not in SUPPORTED_DATABASES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported database type: {request.db_type}. Supported: {SUPPORTED_DATABASES}"
        )

    service = get_database_service()

    success, message, schema = await service.connect_database(
        user_id=request.user_id,
        db_type=request.db_type,
        credentials=request.credentials
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return DatabaseConnectResponse(
        success=True,
        message=message,
        db_type=request.db_type.value,
        schema=schema
    )


@router.get("", response_model=DatabaseListResponse)
async def list_user_databases(
    user_id: str = Query(..., description="User ID to get databases for"),
    _: str = Depends(verify_api_key)
):
    """
    List all databases connected by a user.

    Requires X-API-Key header and user_id query parameter.
    """
    service = get_database_service()
    databases = await service.get_user_databases(user_id)

    return DatabaseListResponse(
        databases=[
            DatabaseInfo(
                db_type=db["db_type"],
                status=db["status"],
                schema=DatabaseSchema(**db["schema"]) if db.get("schema") else None,
                connected_at=db.get("connected_at")
            )
            for db in databases
        ]
    )


@router.post("/disconnect")
async def disconnect_database(
    request: DatabaseDisconnectRequest,
    _: str = Depends(verify_api_key)
):
    """
    Disconnect a database for a user.

    This will remove the stored credentials and connection.

    Requires X-API-Key header.
    """
    service = get_database_service()

    success = await service.disconnect_database(
        user_id=request.user_id,
        db_type=request.db_type
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"No {request.db_type.value} database found for user"
        )

    return {"message": f"{request.db_type.value} database disconnected successfully"}


@router.get("/{db_type}/status")
async def get_database_status(
    db_type: DatabaseType,
    user_id: str = Query(..., description="User ID to check status for"),
    _: str = Depends(verify_api_key)
):
    """
    Get status of a specific database connection.

    Requires X-API-Key header and user_id query parameter.
    """
    service = get_database_service()
    user_db = await service.get_user_database(user_id, db_type)

    if not user_db:
        return {
            "db_type": db_type.value,
            "status": "not_connected"
        }

    return {
        "db_type": db_type.value,
        "status": user_db.get("status", "unknown"),
        "connected_at": user_db.get("connected_at"),
        "schema": user_db.get("schema", {})
    }


@router.get("/{db_type}/schema")
async def get_database_schema(
    db_type: DatabaseType,
    user_id: str = Query(..., description="User ID to get schema for"),
    _: str = Depends(verify_api_key)
):
    """
    Get the schema of a connected database.

    Returns table/collection information including column names and types.

    Requires X-API-Key header and user_id query parameter.
    """
    service = get_database_service()
    user_db = await service.get_user_database(user_id, db_type)

    if not user_db:
        raise HTTPException(
            status_code=404,
            detail=f"No {db_type.value} database connected for user"
        )

    return {
        "db_type": db_type.value,
        "schema": user_db.get("schema", {})
    }
