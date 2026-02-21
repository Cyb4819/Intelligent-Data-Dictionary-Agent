from fastapi import FastAPI
from app.core.logging import setup_logging
from app.api.routes import extract, quality, ai, export, sample
from app.api.middleware import (
    SecurityHeadersMiddleware,
    LoggingMiddleware,
    limiter,
    _rate_limit_exceeded_handler,
    RateLimitExceeded,
)

setup_logging()

app = FastAPI(
    title="Data Dictionary Backend API",
    description="Extract, analyze, and document enterprise database schemas with AI",
    version="1.0.0"
)

# Add middleware (order matters: security first, then logging)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(extract.router, prefix="/api/extract", tags=["schema-extraction"])
app.include_router(quality.router, prefix="/api/quality", tags=["data-quality"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai-features"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(sample.router, prefix="/api/sample", tags=["sample-data"])

@app.get("/healthz", tags=["health"])
async def healthz():
    return {"status": "ok", "service": "data-dictionary-backend"}

