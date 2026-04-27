from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.logging_config import setup_logging
from core.api.routes import router

# Setup logging
logger = setup_logging("core-api")

# Create FastAPI app
app = FastAPI(
    title="Core Service",
    description="Service for processing leads and providing analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, tags=["analytics"])


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Core API service starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Core API service shutting down")


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "core-api"}