"""Database API endpoints for managing user database connections."""
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

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
from ..services.database_service import (
    get_database_service,
    store_database_session,
    get_database_session,
    delete_database_session,
    cleanup_old_database_sessions,
)
from ..config import SUPPORTED_DATABASES, OAUTH_REDIRECT_BASE
from .auth import verify_api_key

router = APIRouter(prefix="/api/databases", tags=["databases"])

# Setup Jinja2 templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Database icons for UI
DB_ICONS = {
    "postgresql": "🐘",
    "mysql": "🐬",
    "mongodb": "🍃",
    "oracle": "🔴",
    "bigquery": "📊",
}


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


# ============================================================================
# Hosted UI Flow Endpoints
# ============================================================================

@router.post("/initiate")
async def initiate_database_connection(
    user_id: str = Query(..., description="User ID initiating connection"),
    db_type: DatabaseType = Query(..., description="Database type to connect"),
    redirect_url: Optional[str] = Query(None, description="URL to redirect after connection"),
    _: str = Depends(verify_api_key)
):
    """
    Initiate a database connection flow.

    Returns a connect_url where the user should be redirected to enter credentials.
    Similar to OAuth flow but for database credentials.

    Requires X-API-Key header.

    Returns:
        - connect_url: URL to redirect user for credential input
        - session_id: Session ID for tracking
        - db_type: Database type
    """
    if db_type.value not in SUPPORTED_DATABASES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported database type: {db_type}. Supported: {SUPPORTED_DATABASES}"
        )

    # Generate session ID
    session_id = str(uuid.uuid4())

    # Store session
    await store_database_session(
        session_id=session_id,
        user_id=user_id,
        db_type=db_type.value,
        redirect_url=redirect_url
    )

    # Cleanup old sessions periodically
    try:
        await cleanup_old_database_sessions(max_age_minutes=30)
    except Exception:
        pass  # Non-critical

    # Build connect URL
    connect_url = f"{OAUTH_REDIRECT_BASE}/api/databases/connect/{session_id}"

    return {
        "connect_url": connect_url,
        "session_id": session_id,
        "db_type": db_type.value
    }


@router.get("/connect/{session_id}", response_class=HTMLResponse)
async def database_connect_page(
    request: Request,
    session_id: str
):
    """
    Hosted UI page for entering database credentials.

    This page is shown to users after they click the connect_url.
    No API key required - session_id provides authentication.
    """
    # Get session
    session = await get_database_session(session_id)
    if not session:
        return templates.TemplateResponse(
            "database_connect.html",
            {
                "request": request,
                "error": "Session expired or invalid. Please try connecting again.",
                "session_id": "",
                "db_display_name": "Database",
                "db_description": "",
                "db_icon": "🗄️",
                "fields": []
            }
        )

    db_type = session["db_type"]

    # Get database type info
    service = get_database_service()
    db_types = service.get_supported_databases()
    db_info = next((db for db in db_types if db.type.value == db_type), None)

    if not db_info:
        return templates.TemplateResponse(
            "database_connect.html",
            {
                "request": request,
                "error": f"Unknown database type: {db_type}",
                "session_id": session_id,
                "db_display_name": db_type,
                "db_description": "",
                "db_icon": "🗄️",
                "fields": []
            }
        )

    return templates.TemplateResponse(
        "database_connect.html",
        {
            "request": request,
            "session_id": session_id,
            "db_display_name": db_info.display_name,
            "db_description": db_info.description,
            "db_icon": DB_ICONS.get(db_type, "🗄️"),
            "fields": [field.model_dump() for field in db_info.fields],
            "error": None
        }
    )


@router.post("/connect/callback")
async def database_connect_callback(
    request: Request,
    session_id: str = Form(...)
):
    """
    Handle credential form submission from hosted UI.

    Tests the connection, saves credentials if successful, and redirects.
    """
    # Get session
    session = await get_database_session(session_id)
    if not session:
        return templates.TemplateResponse(
            "database_connect.html",
            {
                "request": request,
                "error": "Session expired. Please try connecting again.",
                "session_id": "",
                "db_display_name": "Database",
                "db_description": "",
                "db_icon": "🗄️",
                "fields": []
            }
        )

    db_type = session["db_type"]
    user_id = session["user_id"]
    redirect_url = session.get("redirect_url")

    # Get form data
    form_data = await request.form()
    credentials = {}

    # Get database type info for field types
    service = get_database_service()
    db_types = service.get_supported_databases()
    db_info = next((db for db in db_types if db.type.value == db_type), None)

    if db_info:
        for field in db_info.fields:
            value = form_data.get(field.name)
            if field.type == "boolean":
                credentials[field.name] = value == "on" or value == "true"
            elif field.type == "integer" and value:
                credentials[field.name] = int(value)
            elif value:
                credentials[field.name] = value
            elif field.default is not None:
                credentials[field.name] = field.default

    # Test connection and save
    try:
        success, message, schema = await service.connect_database(
            user_id=user_id,
            db_type=DatabaseType(db_type),
            credentials=credentials
        )
    except Exception as e:
        success = False
        message = str(e)
        schema = None

    if not success:
        # Show error on the form
        return templates.TemplateResponse(
            "database_connect.html",
            {
                "request": request,
                "error": message,
                "session_id": session_id,
                "db_display_name": db_info.display_name if db_info else db_type,
                "db_description": db_info.description if db_info else "",
                "db_icon": DB_ICONS.get(db_type, "🗄️"),
                "fields": [field.model_dump() for field in db_info.fields] if db_info else []
            }
        )

    # Success - delete session
    await delete_database_session(session_id)

    # Redirect to client app
    if redirect_url:
        # Append success parameters
        separator = "&" if "?" in redirect_url else "?"
        final_url = f"{redirect_url}{separator}db_type={db_type}&status=connected"
        return RedirectResponse(url=final_url, status_code=302)

    # No redirect URL - show success message
    return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Connection Successful</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    background: white;
                    border-radius: 16px;
                    padding: 40px;
                    text-align: center;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                }}
                .icon {{ font-size: 64px; margin-bottom: 16px; }}
                h1 {{ color: #1a1a2e; margin-bottom: 8px; }}
                p {{ color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">✅</div>
                <h1>{db_info.display_name if db_info else db_type} Connected!</h1>
                <p>You can close this window and return to your application.</p>
            </div>
        </body>
        </html>
    """)
