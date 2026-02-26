from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from collections import defaultdict
from datetime import datetime
import time
import os
import logging

logger=logging.getLogger(__name__)
RATE_LIMIT=int(os.getenv("RATE_LIMIT_REQUESTS", 100))
WINDOW=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", 60))
request_counts: dict=defaultdict(list)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start=time.time()
        response=await call_next(request)
        duration=round((time.time() - start) * 1000, 2)
        logger.info(f"{request.method} {request.url.path} {response.status_code} {duration}ms client={request.client.host}")
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip=request.client.host
        now=time.time()
        request_counts[ip]=[t for t in request_counts[ip] if now - t < WINDOW]
        if len(request_counts[ip]) >= RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for {ip}")
            return JSONResponse(status_code=429, content={"detail": "Too many requests, slow down."})
        request_counts[ip].append(now)
        return await call_next(request)
