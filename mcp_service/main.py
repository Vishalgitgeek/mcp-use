"""MCP Integration Service - Main FastAPI Application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import SERVER_HOST, SERVER_PORT, validate_config
from .db.mongodb import connect_to_mongodb, close_connection, create_indexes
from .api.integrations import router as integrations_router
from .api.tools import router as tools_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting MCP Integration Service...")

    # Validate configuration
    config_errors = validate_config()
    if config_errors:
        for error in config_errors:
            logger.warning(f"Config warning: {error}")

    # Connect to MongoDB
    try:
        await connect_to_mongodb()
        await create_indexes()
        logger.info("Database connected and indexes created")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    logger.info("MCP Integration Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down MCP Integration Service...")
    await close_connection()
    logger.info("MCP Integration Service stopped")


# Create FastAPI app
app = FastAPI(
    title="MCP Integration Service",
    description="""
    Service for managing MCP integrations and exposing tools to AI agents.

    ## Features
    - User integration management (Gmail, Slack, etc.)
    - OAuth connection handling
    - Tool discovery and execution for AI agents

    ## Authentication
    - User endpoints: Bearer token (JWT)
    - Agent endpoints: X-API-Key header
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(integrations_router)
app.include_router(tools_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MCP Integration Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


def run():
    """Run the application."""
    import uvicorn
    uvicorn.run(
        "mcp_service.main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True
    )


if __name__ == "__main__":
    run()
