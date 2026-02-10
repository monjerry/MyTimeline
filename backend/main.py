"""Main FastAPI application for the timeline service."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.api.routes import images, timeline, processing


# Create FastAPI app
app = FastAPI(
    title="Timeline AI API",
    description="API for image timeline with AI analysis",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving images
data_dir = Path("./data")
if data_dir.exists():
    app.mount("/static", StaticFiles(directory=str(data_dir)), name="static")

# Include routers
app.include_router(images.router, prefix="/api", tags=["images"])
app.include_router(timeline.router, prefix="/api", tags=["timeline"])
app.include_router(processing.router, prefix="/api", tags=["processing"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Timeline AI API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
