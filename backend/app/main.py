"""LUXOR9 - Main FastAPI Application"""
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from threading import Lock
from typing import Dict, Tuple

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.routes import (
    agents_router,
    streams_router,
    categories_router,
    system_router,
    metrics_router
)
from app.api.ceo_routes import ceo_router
from app.database import init_async_db, close_async_db, seed_categories_async

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_async_db()
    await seed_categories_async()
    print("═══ LUXOR9 DATABASE INITIALIZED ═══")
    yield
    await close_async_db()
    print("═══ LUXOR9 DATABASE CLOSED ═══")


class RateLimiter:
    """Simple in-memory rate limiter with sliding window"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, list] = defaultdict(list)
        self.hour_requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def _clean_old_requests(self, client_id: str, current_time: float):
        """Remove requests older than window"""
        minute_cutoff = current_time - 60
        hour_cutoff = current_time - 3600
        
        self.minute_requests[client_id] = [
            t for t in self.minute_requests[client_id] if t > minute_cutoff
        ]
        self.hour_requests[client_id] = [
            t for t in self.hour_requests[client_id] if t > hour_cutoff
        ]
    
    def check_rate_limit(self, client_id: str) -> Tuple[bool, dict]:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        with self.lock:
            self._clean_old_requests(client_id, current_time)
            
            minute_count = len(self.minute_requests[client_id])
            hour_count = len(self.hour_requests[client_id])
            
            if minute_count >= self.requests_per_minute:
                return False, {
                    "error": "rate_limit_exceeded",
                    "detail": f"Rate limit: {self.requests_per_minute} requests per minute",
                    "retry_after": int(60 - (current_time - self.minute_requests[client_id][0]))
                }
            
            if hour_count >= self.requests_per_hour:
                return False, {
                    "error": "rate_limit_exceeded",
                    "detail": f"Rate limit: {self.requests_per_hour} requests per hour",
                    "retry_after": int(3600 - (current_time - self.hour_requests[client_id][0]))
                }
            
            # Record this request
            self.minute_requests[client_id].append(current_time)
            self.hour_requests[client_id].append(current_time)
            
            return True, {
                "remaining_minute": self.requests_per_minute - minute_count - 1,
                "remaining_hour": self.requests_per_hour - hour_count - 1
            }


# Initialize rate limiter
rate_limiter = RateLimiter(
    requests_per_minute=settings.rate_limit_per_minute,
    requests_per_hour=settings.rate_limit_per_hour
)


async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests"""
    if not settings.rate_limit_enabled:
        return await call_next(request)
    
    # Skip rate limiting for health checks
    if request.url.path in ["/", "/ping", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Get client identifier
    client_id = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
        request.headers.get("X-Real-IP") or
        request.client.host if request.client else "unknown"
    )
    
    allowed, info = rate_limiter.check_rate_limit(client_id)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content=info,
            headers={"Retry-After": str(info.get("retry_after", 60))}
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Remaining-Minute"] = str(info["remaining_minute"])
    response.headers["X-RateLimit-Remaining-Hour"] = str(info["remaining_hour"])
    
    return response


# Create FastAPI app
app = FastAPI(
    title="LUXOR9 - Hierarchical Agentic AI Orchestration",
    description="API for the LUXOR9 AI agent command center",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)


# Add CORS middleware with secure defaults
if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_methods_list,
        allow_headers=settings.cors_headers_list,
    )
elif settings.is_development:
    # Allow all in development ONLY
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# Production: no CORS middleware = block cross-origin requests


# Add rate limiting
app.middleware("http")(rate_limit_middleware)


# Include routers
app.include_router(agents_router)
app.include_router(streams_router)
app.include_router(categories_router)
app.include_router(system_router)
app.include_router(metrics_router)
app.include_router(ceo_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "LUXOR9 API",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": time.time()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "rate_limiting": settings.rate_limit_enabled,
        "timestamp": time.time()
    }
