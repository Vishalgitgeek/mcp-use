"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, api_routes, ui_routes, diagnostic_routes
from config import SERVER_HOST, SERVER_PORT

# Create FastAPI app
app = FastAPI(title="Local ↔ Drive Sync", version="1.0.0")

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ui_routes.router)
app.include_router(auth_routes.router)
app.include_router(api_routes.router)
app.include_router(diagnostic_routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
