from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api import auth, users, widgets, admin
from app.core.config import settings
from app.core.middleware import add_middleware
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for CRUD operations on widgets with CORS and rate limiting",
    version="1.0.0"
)

# Add middleware (CORS, rate limiting)
add_middleware(app)

# Include routers
app.include_router(auth.router, tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(widgets.router, prefix="/widgets", tags=["widgets"])
app.include_router(admin.router)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with better error messages"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request details"""
    start_time = time.time()
    
    # Get client IP
    client_ip = request.client.host
    
    # Process the request and get the response
    response = await call_next(request)
    
    # Calculate process time
    process_time = time.time() - start_time
    
    # Log the request
    logger.info(
        f"{request.method} {request.url.path} {response.status_code} "
        f"[{client_ip}] - {process_time:.4f}s"
    )
    
    return response

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)