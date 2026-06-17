from __future__ import annotations

import logging
import time
import uuid
from typing import Callable, Awaitable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings

logger = logging.getLogger("backend.middleware")


def register_middleware(app: FastAPI) -> None:
    _add_cors(app)
    _add_request_logging(app)
    _add_global_error_handler(app)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
def _add_cors(app: FastAPI) -> None:
    origins = settings.cors_origins
    logger.info("CORS allowed origins: %s", origins)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )


# ---------------------------------------------------------------------------
# Request logging
# ---------------------------------------------------------------------------
class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


def _add_request_logging(app: FastAPI) -> None:
    app.add_middleware(RequestLogMiddleware)


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
def _add_global_error_handler(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> Response:
        request_id = uuid.uuid4().hex[:12]
        logger.exception(
            "Unhandled exception [%s] on %s %s",
            request_id,
            request.method,
            request.url.path,
        )
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal error",
                "request_id": request_id,
            },
        )
