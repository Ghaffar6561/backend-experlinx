from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .core.config import settings
from .api.v1.health import router as health_router
from .api.v1.auth import router as auth_router
from .api.v1.users import router as users_router
from .api.v1.tools import router as tools_router
from .api.v1.usage import router as usage_router
from .api.v1.subscriptions import router as subscriptions_router
from .api.v1.admin import router as admin_router
from .schemas.common import ApiResponse, ApiError
import logging
import sys
import uuid


# Configure logging
if settings.LOG_FORMAT == "json":
    import json_log_formatter
    formatter = json_log_formatter.JSONFormatter()
    
    # Set up root logger with JSON formatter
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger(None)  # Get root logger
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.addHandler(log_handler)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add a unique request ID to each request for tracing purposes.
    """
    async def dispatch(self, request: Request, call_next):
        # Get request ID from header or generate a new one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Add request ID to the response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown.
    """
    # Startup
    logging.info("Application starting up...")
    
    # Perform any startup tasks here
    # For example: database connection, cache initialization, etc.
    
    yield
    
    # Shutdown
    logging.info("Application shutting down...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Expose X-Request-ID header for tracing
        expose_headers=["X-Request-ID"],
    )
    
    # Add request ID middleware for tracing
    app.add_middleware(RequestIDMiddleware)
    
    # Include API routes
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
    app.include_router(users_router, prefix="/api/v1", tags=["users"])
    app.include_router(tools_router, prefix="/api/v1", tags=["tools"])
    app.include_router(usage_router, prefix="/api/v1", tags=["usage"])
    app.include_router(subscriptions_router, prefix="/api/v1", tags=["subscriptions"])
    app.include_router(admin_router, prefix="/api/v1", tags=["admin"])
    
    # Add exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle validation errors and return a consistent error response format.
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            })
        
        error_response = ApiError(
            code="VALIDATION_ERROR",
            message="Validation failed",
            details=errors
        )
        
        return JSONResponse(
            status_code=422,
            content=ApiResponse(error=error_response.model_dump()).model_dump()
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle HTTP exceptions and return a consistent error response format.
        """
        error_response = ApiError(
            code=f"HTTP_{exc.status_code}",
            message=exc.detail
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(error=error_response.model_dump()).model_dump()
        )
    
    @app.get("/")
    async def root():
        """
        Root endpoint for basic service information.
        """
        return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}"}
    
    return app


# Create the application instance
app = create_app()


# Add any additional configuration or routes after app creation
if __name__ == "main":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )