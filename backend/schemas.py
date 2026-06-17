from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class StatementRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    statement: str = Field(min_length=1, max_length=500)

    @classmethod
    def validate_payload(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Must not be empty or whitespace-only")
        return stripped


class StatementResponse(BaseModel):
    reply: str
    contradiction_detected: bool
    contradicted_opinion: Optional[dict[str, Any]] = None
    new_opinion: dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)


class OpinionOut(BaseModel):
    opinion_id: str
    user_id: str
    topic: str
    statement: str
    stance: str
    timestamp: str
    match_context: Optional[str] = None


class HistoryResponse(BaseModel):
    user_id: str
    opinion_count: int
    opinions: list[OpinionOut]


class TopicHistoryResponse(BaseModel):
    user_id: str
    topic: str
    opinions: list[OpinionOut]


class ContradictionOut(BaseModel):
    old_opinion: dict[str, Any]
    new_opinion: dict[str, Any]
    detected_at: str


class ContradictionsResponse(BaseModel):
    user_id: str
    contradiction_count: int
    contradictions: list[ContradictionOut]


class HealthResponse(BaseModel):
    status: str
    version: str
    agent: str
    reason: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    request_id: Optional[str] = None
