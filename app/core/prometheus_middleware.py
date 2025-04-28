"""
Prometheus middleware for recording request metrics
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.metrics import record_request_metrics, ACTIVE_REQUESTS

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for each request
    """
    
    async def dispatch(self, request: Request, call_next):
        # Increment active requests counter
        ACTIVE_REQUESTS.inc()
        
        # Record start time
        start_time = time.time()
        
        # Get path template if possible
        path_template = request.url.path
        route = request.scope.get("route")
        if route and route.path:
            path_template = route.path
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            record_request_metrics(
                method=request.method,
                endpoint=path_template,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
        except Exception as e:
            # Record metrics for exceptions with 500 status code
            duration = time.time() - start_time
            record_request_metrics(
                method=request.method,
                endpoint=path_template,
                status_code=500,
                duration=duration
            )
            raise e
        finally:
            # Decrement active requests counter
            ACTIVE_REQUESTS.dec()