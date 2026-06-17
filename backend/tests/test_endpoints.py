"""End-to-end tests for Hot Take Tracker backend.

Patches all external dependencies (Walrus, OpenAI, httpx) so tests
run deterministically without live services.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Callable
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Set test env vars BEFORE any code imports config/settings
# ---------------------------------------------------------------------------
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake-key-for-testing")
os.environ.setdefault("WALRUS_PUBLISHER", "https://publisher.test")
os.environ.setdefault("WALRUS_AGGREGATOR", "https://aggregator.test")

# ---------------------------------------------------------------------------
# Ensure ai-agent is on sys.path *before* any imports from it
# ---------------------------------------------------------------------------
_AI_AGENT = str(Path(__file__).resolve().parent.parent.parent / "ai-agent")
if _AI_AGENT not in sys.path:
    sys.path.insert(0, _AI_AGENT)

# Now safe to import from ai-agent modules
from models import UserMemory, Opinion, ContradictionEvent

# ---------------------------------------------------------------------------
# In-memory Walrus store  (replaces store_memory / read_memory)
# ---------------------------------------------------------------------------
_walrus_data: dict[str, dict[str, Any]] = {}
_walrus_counter: int = 0


def _mock_store_memory(data: dict[str, Any], publisher_url: str = "") -> str:
    global _walrus_counter
    _walrus_counter += 1
    blob_id = f"test_blob_{_walrus_counter}"
    _walrus_data[blob_id] = data
    return blob_id


def _mock_read_memory(blob_id: str, aggregator_url: str = "") -> dict[str, Any]:
    from exceptions import WalrusReadError

    if blob_id not in _walrus_data:
        raise WalrusReadError(blob_id, "not found in test store")
    return _walrus_data[blob_id]


def _reset_walrus() -> None:
    _walrus_data.clear()
    global _walrus_counter
    _walrus_counter = 0


# ---------------------------------------------------------------------------
# Topic-extraction mock  (deterministic, no OpenAI call)
# ---------------------------------------------------------------------------
def _mock_extract_topic(
    statement: str, client: Any, model: str = ""
) -> tuple[str, str]:
    text = statement.strip().lower()

    if "france" in text:
        if any(w in text for w in ("struggle", "bad", "overrated", "won't")):
            return ("France", "negative")
        return ("France", "positive")
    if "brazil" in text:
        if any(w in text for w in ("win", "strong", "best", "great")):
            return ("Brazil", "positive")
        return ("Brazil", "negative")
    if "portugal" in text:
        return ("Portugal", "positive")
    if "argentina" in text:
        return ("Argentina", "positive")
    if "germany" in text:
        return ("Germany", "negative")
    return ("unknown", "neutral")


# ---------------------------------------------------------------------------
# Pytest fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _test_db() -> None:
    """Replace the global SQLite connection with a fresh in-memory one."""
    import db

    db._connection = None
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS blob_registry (
            user_id     TEXT PRIMARY KEY,
            blob_id     TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        )"""
    )
    conn.commit()
    db._connection = conn
    yield
    db._connection = None


@pytest.fixture(autouse=True)
def _reset_globals() -> None:
    """Reset module-level state that carries between tests."""
    import main as main_module

    main_module._agent = None
    main_module._blob_registry.clear()
    _reset_walrus()


@pytest.fixture(autouse=True)
def _patch_externals() -> Any:
    """Mock all external I/O so tests are hermetic."""
    from agent import HotTakeAgent

    patches = [
        # Walrus
        patch("memory_store.store_memory", side_effect=_mock_store_memory),
        patch("memory_store.read_memory", side_effect=_mock_read_memory),
        # Agent-level references (agent.py imports these at module top)
        patch("agent.get_user_memory", side_effect=_mock_get_user_memory),
        patch("agent.save_user_memory", side_effect=_mock_save_user_memory),
        patch("agent.extract_topic", side_effect=_mock_extract_topic),
        # Reply generation (avoids real OpenAI call)
        patch.object(HotTakeAgent, "_generate_reply", return_value="Noted."),
        # Startup health checks
        patch("httpx.get", return_value=MagicMock(is_success=True)),
        patch("openai.OpenAI"),
    ]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.fixture
def client() -> Any:
    """Return a TestClient instance.  Lifespan runs on enter/exit."""
    from main import app

    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Helper — issues POST /api/statement and returns JSON
# ---------------------------------------------------------------------------
def _post(
    client: TestClient, user_id: str, statement: str
) -> Any:
    return client.post(
        "/api/statement",
        json={"user_id": user_id, "statement": statement},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestHealthCheck:
    def test_health_check_returns_ok(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["version"] == "1.0.0"
        assert body["agent"] == "ready"


class TestStatement:
    def test_statement_new_topic_no_contradiction(
        self, client: TestClient
    ) -> None:
        resp = _post(client, "user_new", "Portugal will surprise everyone")
        assert resp.status_code == 200
        body = resp.json()
        assert body["contradiction_detected"] is False
        assert body["new_opinion"]["topic"] == "Portugal"
        assert body["contradicted_opinion"] is None

    def test_statement_consistent_with_history(
        self, client: TestClient
    ) -> None:
        _post(client, "user_cons", "Brazil will win Group C")
        resp = _post(client, "user_cons", "Brazil looking strong in Group C")
        assert resp.status_code == 200
        body = resp.json()
        assert body["contradiction_detected"] is False

    def test_statement_contradicts_history(
        self, client: TestClient
    ) -> None:
        r1 = _post(client, "user_contra", "France will struggle this tournament")
        assert r1.status_code == 200
        first_stmt = r1.json()["new_opinion"]["statement"]

        r2 = _post(client, "user_contra", "France is the best team here")
        assert r2.status_code == 200
        body = r2.json()
        assert body["contradiction_detected"] is True
        assert body["contradicted_opinion"] is not None
        assert body["contradicted_opinion"]["statement"] == first_stmt

    def test_empty_statement_rejected(self, client: TestClient) -> None:
        resp = client.post(
            "/api/statement",
            json={"user_id": "u1", "statement": "   "},
        )
        assert resp.status_code == 422

    def test_statement_too_long_rejected(self, client: TestClient) -> None:
        long_text = "x" * 501
        resp = client.post(
            "/api/statement",
            json={"user_id": "u1", "statement": long_text},
        )
        assert resp.status_code == 422


class TestHistory:
    def test_history_endpoint_new_user_returns_empty_list(
        self, client: TestClient
    ) -> None:
        resp = client.get("/api/history/never_seen_user_42")
        assert resp.status_code == 200
        body = resp.json()
        assert body["opinions"] == []

    def test_history_endpoint_returns_chronological_order(
        self, client: TestClient
    ) -> None:
        _post(client, "user_hist", "First take")
        _post(client, "user_hist", "Second take")
        _post(client, "user_hist", "Third take")

        resp = client.get("/api/history/user_hist")
        assert resp.status_code == 200
        body = resp.json()
        assert body["opinion_count"] == 3
        stmts = [o["statement"] for o in body["opinions"]]
        # Newest first
        assert stmts == ["Third take", "Second take", "First take"]


class TestContradictions:
    def test_contradictions_endpoint_empty_for_consistent_user(
        self, client: TestClient
    ) -> None:
        _post(client, "user_consistent", "Argentina is looking great")
        _post(client, "user_consistent", "Argentina will go far")

        resp = client.get("/api/contradictions/user_consistent")
        assert resp.status_code == 200
        body = resp.json()
        assert body["contradiction_count"] == 0
        assert body["contradictions"] == []

    def test_contradictions_endpoint_counts_correctly(
        self, client: TestClient
    ) -> None:
        # Two contradictions on different topics
        _post(client, "user_contra2", "France will struggle this tournament")
        _post(client, "user_contra2", "France is the best team here")

        _post(client, "user_contra2", "Brazil will win Group C")
        _post(client, "user_contra2", "Brazil looking weak in Group C")

        resp = client.get("/api/contradictions/user_contra2")
        assert resp.status_code == 200
        body = resp.json()
        assert body["contradiction_count"] == 2


class TestResilience:
    def test_walrus_failure_does_not_crash_request(
        self, client: TestClient
    ) -> None:
        from agent import HotTakeAgent

        from exceptions import WalrusStoreError

        with patch.object(
            HotTakeAgent,
            "_generate_reply",
            return_value="Fallback reply.",
        ), patch(
            "agent.get_user_memory",
            side_effect=_mock_get_user_memory,  # keep memory working
        ), patch(
            "agent.save_user_memory",
            side_effect=WalrusStoreError(500, "Simulated write failure"),
        ):
            resp = _post(
                client, "user_503", "Germany won't make it past groups"
            )
            # Should still get a 200 because the agent catches the persistence
            # failure and degrades gracefully.
            assert resp.status_code == 200

    def test_concurrent_users_have_isolated_memory(
        self, client: TestClient
    ) -> None:
        # User A: positive on France
        _post(client, "user_a", "France is incredible this year")

        # User B: negative on France
        _post(client, "user_b", "France is overrated")

        r2 = _post(client, "user_a", "France will win it all")
        assert r2.status_code == 200
        body_a = r2.json()
        # User A has been consistently positive — no contradiction
        assert body_a["contradiction_detected"] is False

        r3 = _post(client, "user_b", "France is actually good")
        assert r3.status_code == 200
        body_b = r3.json()
        # User B was negative, now positive — contradiction!
        assert body_b["contradiction_detected"] is True

    def test_statement_contradicts_history_exact_quote(
        self, client: TestClient
    ) -> None:
        """Verify that the contradicted_opinion.statement is the *exact* original text."""
        r1 = _post(client, "user_quote", "France will struggle this tournament compared to 2018")
        assert r1.status_code == 200
        exact_original = r1.json()["new_opinion"]["statement"]

        r2 = _post(client, "user_quote", "France is the best team here, no doubt")
        assert r2.status_code == 200
        body = r2.json()
        assert body["contradicted_opinion"]["statement"] == exact_original


# ---------------------------------------------------------------------------
# Helpers defined after classes so they can reference mocked module attrs
# ---------------------------------------------------------------------------
def _mock_get_user_memory(
    user_id: str, blob_registry: dict[str, str], aggregator_url: str = ""
) -> UserMemory:
    """Read from the in-memory Walrus store, or return fresh memory."""
    blob_id = blob_registry.get(user_id)
    if blob_id is None:
        return UserMemory(user_id=user_id)

    raw = _walrus_data.get(blob_id)
    if raw is None:
        return UserMemory(user_id=user_id)

    opinions = [Opinion(**o) for o in raw.get("opinions", [])]
    contradictions = [
        ContradictionEvent(**c) for c in raw.get("contradictions", [])
    ]
    return UserMemory(
        user_id=user_id,
        opinions=opinions,
        contradictions=contradictions,
        blob_id=blob_id,
    )


def _mock_save_user_memory(memory: UserMemory, publisher_url: str = "") -> str:
    """Write to the in-memory Walrus store and return a blob_id."""
    data = memory.model_dump(mode="json")
    return _mock_store_memory(data, publisher_url)
