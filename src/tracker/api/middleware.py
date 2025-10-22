"""API middleware for logging, error handling, and request processing"""

import logging
import time
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("tracker.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details
        
        Logs:
        - Request method, path, client IP
        - Response status code
        - Request duration
        """
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"-> {response.status_code} ({duration:.3f}s)"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Handle unexpected errors with standard JSON responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Catch unhandled exceptions and return standard error responses
        
        Returns JSON with:
        - success: false
        - error: error message
        - detail: detailed error info (in debug mode)
        """
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "error": "Validation error",
                    "detail": str(e)
                }
            )
        except PermissionError as e:
            logger.warning(f"Permission denied: {e}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "success": False,
                    "error": "Permission denied",
                    "detail": str(e)
                }
            )
        except FileNotFoundError as e:
            logger.warning(f"Resource not found: {e}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "error": "Resource not found",
                    "detail": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred"
                }
            )


def setup_logging():
    """Configure logging for the API"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Set specific log levels
    logging.getLogger("tracker.api").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce noise
