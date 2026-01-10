"""FastAPI Main Application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
import structlog

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.core.exceptions import (
    AppException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ValidationException,
)

# Setup structured logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting CustomerLLM Backend", version=settings.APP_VERSION)
    
    # Initialize Qdrant collections
    from app.services.vector.qdrant_service import QdrantService
    qdrant_service = QdrantService()
    await qdrant_service.initialize_collections()
    
    # Initialize PVC storage directories
    from app.services.storage.file_storage import FileStorage
    FileStorage().ensure_dirs()


    # Verify vLLM connectivity
    from app.services.inference.vllm_service import VLLMService
    vllm_service = VLLMService()
    if not await vllm_service.health_check():
        logger.error("vLLM health check failed")
        raise RuntimeError("vLLM is unavailable")


    #logger.info("Skipping vLLM health check at startup")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CustomerLLM Backend")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI Chat & Document Intelligence Platform",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Prometheus Instrumentation
if settings.PROMETHEUS_ENABLED:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.error(
        "Application error",
        error=str(exc),
        status_code=exc.status_code,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": exc.__class__.__name__},
    )


@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    return JSONResponse(
        status_code=401,
        content={"detail": exc.detail, "type": "AuthenticationError"},
    )


@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(request: Request, exc: AuthorizationException):
    return JSONResponse(
        status_code=403,
        content={"detail": exc.detail, "type": "AuthorizationError"},
    )


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.detail, "type": "NotFoundError"},
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.detail, "type": "ValidationError"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "InternalError"},
    )


# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    from app.services.inference.vllm_service import VLLMService
    from app.services.vector.qdrant_service import QdrantService

    checks = {
        "vllm": await VLLMService().health_check(),
    }
    try:
        await QdrantService().get_collection_info()
        checks["qdrant"] = True
    except Exception:
        checks["qdrant"] = False

    ready = all(checks.values())
    return {"ready": ready, "checks": checks}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else None,
    }


# Include API Router
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )

