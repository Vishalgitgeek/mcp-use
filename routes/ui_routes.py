"""UI routes for serving the web interface."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from templates.index import get_index_html

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web UI."""
    return HTMLResponse(content=get_index_html())

