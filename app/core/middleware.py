from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List, Set, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory store for rate limiting
# This is a simple implementation. For production, use Redis or another distributed cache
class RateLimiter:
    def __init__(self):
        self.ip_cache: Dict[str, List[datetime]] = {}
        self.token_cache: Dict[str, List[datetime]] = {}
        self.cleanup_counter = 0
    
    def _cleanup_old_requests(self, cache: Dict[str, List[datetime]]) -> None:
        """Remove timestamps older than the rate limit window"""
        now = datetime.utcnow()
        window_time = now - timedelta(seconds=settings.RATE_LIMIT_WINDOW_SECONDS)
        
        for key in list(cache.keys()):
            cache[key] = [ts for ts in cache[key] if ts > window_time]
            # Remove entries with no timestamps
            if not cache[key]:
                del cache[key]
    
    def is_rate_limited(
        self, 
        ip: str, 
        token: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is rate limited
        Returns (is_limited, headers)
        """
        now = datetime.utcnow()
        
        # Periodically clean up old requests to prevent memory growth
        self.cleanup_counter += 1
        if self.cleanup_counter > 100:
            self._cleanup_old_requests(self.ip_cache)
            self._cleanup_old_requests(self.token_cache)
            self.cleanup_counter = 0
        
        # Check IP-based rate limiting
        ip_requests = self.ip_cache.get(ip, [])
        window_time = now - timedelta(seconds=settings.RATE_LIMIT_WINDOW_SECONDS)
        ip_requests = [ts for ts in ip_requests if ts > window_time]
        
        # Check token-based rate limiting if token is provided
        token_requests = []
        if token:
            token_requests = self.token_cache.get(token, [])
            token_requests = [ts for ts in token_requests if ts > window_time]
        
        # Determine which limit to apply (IP or token)
        if token and len(token_requests) >= settings.RATE_LIMIT_AUTH_REQUESTS:
            # Authenticated user exceeded their limit
            remaining = 0
            limit = settings.RATE_LIMIT_AUTH_REQUESTS
            is_limited = True
        elif not token and len(ip_requests) >= settings.RATE_LIMIT_ANON_REQUESTS:
            # Anonymous user exceeded their limit
            remaining = 0
            limit = settings.RATE_LIMIT_ANON_REQUESTS
            is_limited = True
        else:
            # Not rate limited
            if token:
                remaining = settings.RATE_LIMIT_AUTH_REQUESTS - len(token_requests)
                limit = settings.RATE_LIMIT_AUTH_REQUESTS
            else:
                remaining = settings.RATE_LIMIT_ANON_REQUESTS - len(ip_requests)
                limit = settings.RATE_LIMIT_ANON_REQUESTS
            
            # Record this request
            if token:
                if token not in self.token_cache:
                    self.token_cache[token] = []
                self.token_cache[token].append(now)
            
            if ip not in self.ip_cache:
                self.ip_cache[ip] = []
            self.ip_cache[ip].append(now)
            
            is_limited = False
        
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, remaining)),
            "X-RateLimit-Reset": str(int((window_time + timedelta(seconds=settings.RATE_LIMIT_WINDOW_SECONDS)).timestamp()))
        }
        
        return is_limited, headers


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.limiter = RateLimiter()
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths if needed
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path == "/health":
            return await call_next(request)
        
        # Get the client's IP address
        ip = request.client.host
        
        # Extract the auth token if present
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Check if the request is rate limited
        is_limited, headers = self.limiter.is_rate_limited(ip, token)
        
        if is_limited:
            # Return a 429 Too Many Requests response
            return Response(
                content='{"detail": "Too many requests"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers=headers
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to the response
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


def add_middleware(app: FastAPI) -> None:
    """Add all middleware to the FastAPI application"""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        max_age=settings.CORS_MAX_AGE
    )
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)