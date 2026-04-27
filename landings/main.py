from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from shared.logging_config import setup_logging
from landings.api.routes import router

# Setup logging
logger = setup_logging("landings")

# Security scheme for Swagger UI
security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="Landings Service",
    description="Service for accepting leads from landing pages",
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
app.include_router(router, tags=["leads"])


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Landings service starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Landings service shutting down")


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "landings"}
