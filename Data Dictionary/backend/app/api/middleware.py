from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.config import settings
from app.core.logging import logger

# Try to import slowapi; if unavailable provide a no-op fallback so the
# application can run without the package installed (useful for local dev).
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi import _rate_limit_exceeded_handler

    limiter = Limiter(key_func=get_remote_address)
except Exception:  # pragma: no cover - optional dependency
    def get_remote_address(request: Request):
        try:
            return request.client.host
        except Exception:
            return "unknown"

    class RateLimitExceeded(Exception):
        pass

    async def _rate_limit_exceeded_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests (rate limiter not installed)"})

    class _NoOpLimiter:
        def limit(self, *args, **kwargs):
            def _decorator(func):
                return func
            return _decorator

    limiter = _NoOpLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        # Rate limiting is applied via decorators; this is a fallback.
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # OWASP security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            logger.info(f"{request.method} {request.url.path} {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Request error: {str(e)}", exc_info=True)
            raise
