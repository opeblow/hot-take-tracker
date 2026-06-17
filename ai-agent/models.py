from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Opinion(BaseModel):
    opinion_id: str = Field(default_factory=lambda: uuid4().hex[:16])
    user_id: str
    topic: str
    statement: str
    stance: str  # "positive" | "negative" | "neutral"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    match_context: Optional[str] = None


class ContradictionEvent(BaseModel):
    old_opinion: Opinion
    new_opinion: Opinion
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UserMemory(BaseModel):
    user_id: str
    opinions: list[Opinion] = []
    contradictions: list[ContradictionEvent] = []
    blob_id: Optional[str] = None


class AgentResponse(BaseModel):
    reply: str
    contradiction_detected: bool
    contradicted_opinion: Optional[Opinion] = None
    new_opinion: Opinion
    confidence: float = Field(ge=0.0, le=1.0)
