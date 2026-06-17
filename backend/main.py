from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Optional

import httpx
from fastapi import FastAPI, HTTPException
from openai import OpenAI

from config import settings
from db import get_blob_id, init_db, set_blob_id
from middleware import register_middleware
from schemas import (
    ContradictionOut,
    ContradictionsResponse,
    ErrorResponse,
    HealthResponse,
    HistoryResponse,
    OpinionOut,
    StatementRequest,
    StatementResponse,
    TopicHistoryResponse,
)

# ---------------------------------------------------------------------------
# Import ai-agent (hyphenated folder — use sys.path + absolute import)
# ---------------------------------------------------------------------------
_AGENT_DIR = Path(__file__).resolve().parent.parent / "ai-agent"
sys.path.insert(0, str(_AGENT_DIR))

from models import UserMemory  # noqa: E402
from agent import HotTakeAgent  # noqa: E402
from exceptions import (  # noqa: E402
    TopicExtractionError,
    WalrusReadError,
    WalrusStoreError,
    WalrusTimeoutError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Agent instance (lazy-created after lifespan starts)
# ---------------------------------------------------------------------------
_agent: Optional[HotTakeAgent] = None
_blob_registry: dict[str, str] = {}


def get_agent() -> HotTakeAgent:
    global _agent
    if _agent is None:
        _agent = HotTakeAgent(
            openai_client=OpenAI(api_key=settings.openai_api_key),
            blob_registry=_blob_registry,
            publisher_url=settings.walrus_publisher,
            aggregator_url=settings.walrus_aggregator,
        )
    return _agent


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting Hot Take Tracker backend")
    init_db()
    _validate_startup_checks()
    yield
    logger.info("Shutting down Hot Take Tracker backend")


def _validate_startup_checks() -> None:
    """Log warnings for unreachable services but allow the app to start."""
    try:
        resp = httpx.get(
            f"{settings.walrus_aggregator}/v1/blobs",
            timeout=5,
        )
        if resp.is_success:
            logger.info("Walrus aggregator reachable at %s", settings.walrus_aggregator)
        else:
            logger.warning("Walrus aggregator returned HTTP %d", resp.status_code)
    except Exception as exc:
        logger.warning("Walrus aggregator unreachable at startup: %s", exc)

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        client.models.list(timeout=5)
        logger.info("OpenAI API reachable at startup")
    except Exception as exc:
        logger.warning("OpenAI API unreachable at startup: %s", exc)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Hot Take Tracker",
    version="1.0.0",
    lifespan=lifespan,
)

register_middleware(app)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    checks: list[str] = []
    healthy = True

    try:
        resp = httpx.get(
            f"{settings.walrus_aggregator}/v1/blobs",
            timeout=5,
        )
        if not resp.is_success:
            healthy = False
            checks.append("Walrus aggregator unreachable")
    except Exception:
        healthy = False
        checks.append("Walrus aggregator unreachable")

    if not settings.openai_api_key.startswith("sk-"):
        healthy = False
        checks.append("Invalid OpenAI key format")

    if healthy:
        return HealthResponse(status="ok", version="1.0.0", agent="ready")

    return HealthResponse(
        status="degraded",
        version="1.0.0",
        agent="ready",
        reason="; ".join(checks),
    )


@app.post(
    "/api/statement",
    response_model=StatementResponse,
    responses={422: {"model": ErrorResponse}, 502: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def post_statement(body: StatementRequest) -> StatementResponse:
    user_id = body.user_id.strip()
    statement = body.statement.strip()

    if not user_id or not statement:
        raise HTTPException(
            status_code=422,
            detail={"error": "user_id and statement must not be empty"},
        )

    # Sync the in-memory registry from SQLite before calling the agent
    saved_blob_id = get_blob_id(user_id)
    if saved_blob_id is not None:
        _blob_registry[user_id] = saved_blob_id
    elif user_id in _blob_registry:
        del _blob_registry[user_id]

    agent = get_agent()

    try:
        result = agent.process_statement(user_id, statement)
    except TopicExtractionError:
        logger.exception("Topic extraction failed for user '%s'", user_id)
        raise HTTPException(
            status_code=502,
            detail={"error": "Failed to analyze statement content"},
        )
    except (WalrusStoreError, WalrusReadError, WalrusTimeoutError) as exc:
        logger.exception("Walrus error for user '%s'", user_id)
        raise HTTPException(
            status_code=503,
            detail={"error": "Memory service temporarily unavailable, your message was not saved"},
        )

    # Persist the updated blob_id from agent's in-memory registry
    new_blob_id = _blob_registry.get(user_id)
    if new_blob_id is not None:
        set_blob_id(user_id, new_blob_id)

    return StatementResponse(
        reply=result.reply,
        contradiction_detected=result.contradiction_detected,
        contradicted_opinion=(
            result.contradicted_opinion.model_dump(mode="json")
            if result.contradicted_opinion is not None
            else None
        ),
        new_opinion=result.new_opinion.model_dump(mode="json"),
        confidence=result.confidence,
    )


@app.get(
    "/api/history/{user_id}",
    response_model=HistoryResponse,
    responses={200: {"description": "User history (may be empty)"}},
)
async def get_history(user_id: str) -> HistoryResponse:
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(status_code=422, detail={"error": "user_id must not be empty"})

    saved_blob_id = get_blob_id(user_id)
    if saved_blob_id is not None:
        _blob_registry[user_id] = saved_blob_id

    from memory_store import get_user_memory

    memory = get_user_memory(user_id, _blob_registry, settings.walrus_aggregator)

    opinions_sorted = sorted(
        memory.opinions,
        key=lambda o: o.timestamp,
        reverse=True,
    )

    return HistoryResponse(
        user_id=user_id,
        opinion_count=len(opinions_sorted),
        opinions=[OpinionOut(**o.model_dump(mode="json")) for o in opinions_sorted],
    )


@app.get(
    "/api/topic/{user_id}/{topic}",
    response_model=TopicHistoryResponse,
)
async def get_topic_history(user_id: str, topic: str) -> TopicHistoryResponse:
    user_id = user_id.strip()
    topic = topic.strip()
    if not user_id or not topic:
        raise HTTPException(status_code=422, detail={"error": "user_id and topic must not be empty"})

    saved_blob_id = get_blob_id(user_id)
    if saved_blob_id is not None:
        _blob_registry[user_id] = saved_blob_id

    from memory_store import get_user_memory

    memory = get_user_memory(user_id, _blob_registry, settings.walrus_aggregator)

    from contradiction import _topics_match

    filtered = [
        o
        for o in memory.opinions
        if _topics_match(o.topic, topic)
    ]
    filtered.sort(key=lambda o: o.timestamp, reverse=True)

    return TopicHistoryResponse(
        user_id=user_id,
        topic=topic,
        opinions=[OpinionOut(**o.model_dump(mode="json")) for o in filtered],
    )


@app.get(
    "/api/contradictions/{user_id}",
    response_model=ContradictionsResponse,
)
async def get_contradictions(user_id: str) -> ContradictionsResponse:
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(status_code=422, detail={"error": "user_id must not be empty"})

    saved_blob_id = get_blob_id(user_id)
    if saved_blob_id is not None:
        _blob_registry[user_id] = saved_blob_id

    from memory_store import get_user_memory

    memory = get_user_memory(user_id, _blob_registry, settings.walrus_aggregator)

    contradictions = [
        ContradictionOut(
            old_opinion=c.old_opinion.model_dump(mode="json"),
            new_opinion=c.new_opinion.model_dump(mode="json"),
            detected_at=c.detected_at,
        )
        for c in reversed(memory.contradictions)
    ]

    return ContradictionsResponse(
        user_id=user_id,
        contradiction_count=len(contradictions),
        contradictions=contradictions,
    )
