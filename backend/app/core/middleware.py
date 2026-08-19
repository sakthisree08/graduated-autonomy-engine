"""
Middleware for monitoring and logging
"""

import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics and logs"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={'request_id': request_id}
        )
        
        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", extra={'request_id': request_id})
            raise
        finally:
            # Log response
            duration = time.time() - start_time
            logger.info(
                f"Request completed: {status_code} in {duration:.3f}s",
                extra={'request_id': request_id}
            )
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id
        
        return response