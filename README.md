<div align="center">

  <svg width="160" height="160" viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Hot Take Tracker Logo">
    <rect width="160" height="160" rx="32" fill="#09090B"/>
    <path d="M80 20C68 20 58 30 58 42C58 54 68 64 80 64C92 64 102 54 102 42C102 30 92 20 80 20Z" fill="#EF4444" opacity="0.4"/>
    <path d="M80 30C72 30 66 36 66 44C66 52 72 58 80 58C88 58 94 52 94 44C94 36 88 30 80 30Z" fill="#EF4444"/>
    <path d="M80 44L92 76L80 70L68 76L80 44Z" fill="#6366F1"/>
    <path d="M48 88C40 88 34 94 34 102C34 110 40 116 48 116C56 116 62 110 62 102C62 94 56 88 48 88Z" fill="#EF4444" opacity="0.3"/>
    <path d="M112 88C104 88 98 94 98 102C98 110 104 116 112 116C120 116 126 110 126 102C126 94 120 88 112 88Z" fill="#EF4444" opacity="0.3"/>
    <path d="M48 102L54 120L48 116L42 120L48 102Z" fill="#6366F1" opacity="0.8"/>
    <path d="M112 102L118 120L112 116L106 120L112 102Z" fill="#6366F1" opacity="0.8"/>
    <path d="M80 72V130" stroke="#EF4444" stroke-width="3" stroke-linecap="round"/>
    <path d="M80 130L68 118" stroke="#6366F1" stroke-width="3" stroke-linecap="round"/>
    <path d="M80 130L92 118" stroke="#6366F1" stroke-width="3" stroke-linecap="round"/>
    <circle cx="80" cy="140" r="6" fill="#EF4444"/>
    <path d="M74 140L80 134L86 140L80 146L74 140Z" fill="#6366F1" opacity="0.6"/>
  </svg>

  # Hot Take Tracker

  AI-powered opinion contradiction detector for FIFA World Cup 2026.
  Persistent memory via [Walrus](https://walrus.sui.io), zero placeholder code.

  [![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![React 19](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev)
  [![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)](https://vite.dev)
  [![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
  [![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
  [![OpenAI](https://img.shields.io/badge/OpenAI-Structured_Outputs-412991?logo=openai&logoColor=white)](https://openai.com)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Tests: 13/13](https://img.shields.io/badge/Tests-13%2F13-passing-22c55e)]()

</div>

---

## Overview

Hot Take Tracker is a full-stack AI agent that ingests user opinions about the 2026 FIFA World Cup, stores them on the Walrus decentralized storage protocol, and automatically detects contradictions when users change their stance on teams or players.

The system is composed of three independently deployable modules:

- **ai-agent** -- Core intelligence: OpenAI structured topic extraction, deterministic contradiction logic, Walrus persistence with graceful degradation.
- **backend** -- FastAPI HTTP API: five endpoints, SQLite blob-registry, CORS middleware, global error handling, request logging, startup health checks.
- **frontend** -- React SPA: typing animation, auto-scrolling feed, contradiction cards with entrance animation, skeleton loading, comprehensive error states.

---

## Architecture

```
User Statement
     |
     v
+------------------+     +------------------+     +------------------+
|   React SPA      |---->|   FastAPI API     |---->|   ai-agent       |
|  (Vite + Tailwind)|    |  (5 endpoints)    |    |  (process pipeline)|
+------------------+     +------------------+     +------------------+
                               |                         |
                               v                         v
                         +----------+           +------------------+
                         |  SQLite   |           |  Walrus Protocol |
                         | blob_reg |           | (decentralized)  |
                         +----------+           +------------------+
```

### Data Flow

1. User submits a statement through the SPA.
2. FastAPI delegates to `HotTakeAgent.process_statement`.
3. Agent loads prior opinions from Walrus via blob registry lookup.
4. OpenAI extracts `(topic, stance)` via structured outputs.
5. Deterministic contradiction engine compares stance against history.
6. Contradiction events are recorded inside the user's memory blob.
7. Updated memory is persisted to Walrus; new blob_id stored in SQLite.
8. Agent generates a natural-language reply (with or without contradiction mention).
9. Response flows back through API and SPA for rendering.

---

## Features

- **Structured Topic Extraction** -- Uses OpenAI function-calling to extract structured `(topic, stance)` tuples from free-text opinions.
- **Deterministic Contradiction Detection** -- Pure-logic stance comparison matrix; no ML hallucination, every contradiction is provably correct given the extracted stances.
- **Walrus Persistent Memory** -- All user opinion history and contradiction events stored on the Walrus decentralized storage protocol. Blob IDs are tracked in a lightweight SQLite registry.
- **Graceful Degradation** -- If Walrus is unreachable, the agent still generates a reply. If OpenAI fails, the agent returns a fallback response. No endpoint returns 5xx for transient external failures.
- **Comprehensive Error Handling** -- Five custom exception classes, global FastAPI error handler with `request_id` in every error response, five distinct frontend error states (empty, network, validation, server, slow).
- **Separate Loading States** -- The frontend uses independent flags for AI reply loading, history loading, contradictions loading, and receipt verification. A "still thinking" indicator appears after 8 seconds.
- **Production-Grade Middleware** -- Request logging with timing, CORS restricted to configured origin, startup health checks with non-blocking warnings.
- **Hermetic Test Suite** -- 13 pytest tests with in-memory Walrus store, in-memory SQLite, and mocked OpenAI. No live services required. Every endpoint tested for happy path and edge cases.

---

## Tech Stack

| Layer          | Technology                                  |
|----------------|---------------------------------------------|
| AI Agent       | Python 3.14, OpenAI SDK, Pydantic v2        |
| Backend        | FastAPI 0.115, Uvicorn, SQLite 3, httpx      |
| Frontend       | React 19, Vite 5, Tailwind CSS 3, Framer Motion 11, Axios 1, date-fns 3 |
| Storage        | Walrus (decentralized), SQLite (local index) |
| Testing        | pytest 9, httpx TestClient, unittest.mock    |

---

## Project Structure

```
hot-take-tracker/
|
+-- ai-agent/                      # Core AI agent package
|   +-- __init__.py                # Package exports, logging setup
|   +-- agent.py                   # HotTakeAgent.process_statement pipeline
|   +-- models.py                  # Opinion, UserMemory, ContradictionEvent, AgentResponse
|   +-- memory_store.py            # Walrus read/write, get/save user memory
|   +-- topic_extractor.py         # OpenAI structured output extraction
|   +-- contradiction.py           # Deterministic stance comparison
|   +-- prompts.py                 # System prompts and schemas
|   +-- exceptions.py              # Five custom exception classes
|   +-- requirements.txt           # Package dependencies
|
+-- backend/                       # FastAPI HTTP server
|   +-- main.py                    # App factory, 5 endpoints, startup checks
|   +-- config.py                  # Pydantic Settings with validation
|   +-- db.py                      # SQLite blob registry operations
|   +-- schemas.py                 # Pydantic request/response models
|   +-- middleware.py              # CORS, request logging, global error handler
|   +-- requirements.txt           # Package dependencies
|   +-- .env.example               # Environment variable template
|   +-- tests/
|       +-- __init__.py
|       +-- test_endpoints.py      # 13 hermetic end-to-end tests
|
+-- frontend/                      # React SPA
|   +-- src/
|   |   +-- main.jsx               # Entry point
|   |   +-- App.jsx                # Root layout, state wiring
|   |   +-- config.js              # API origin, constant limits
|   |   +-- index.css              # Tailwind directives, base styles
|   |   +-- hooks/
|   |   |   +-- useHotTake.js      # All API calls, 5 error types, loading flags
|   |   +-- components/
|   |       +-- StatementInput.jsx  # Text area with auto-resize, validation
|   |       +-- ConversationFeed.jsx # Message list with typing effect, auto-scroll
|   |       +-- ContradictionCard.jsx # Flip-card with scale+fade entrance
|   |       +-- ReceiptsPanel.jsx   # Slide-in drawer with skeleton loading
|   |       +-- ui/
|   |           +-- Button.jsx      # Reusable button with loading spinner
|   |           +-- Skeleton.jsx    # Pulse-animated placeholder blocks
|   |           +-- ErrorBanner.jsx # Dismissible error banner
|   +-- index.html
|   +-- vite.config.js
|   +-- tailwind.config.js
|   +-- package.json
|
+-- .gitignore
+-- README.md
```

---

## Quick Start

### Prerequisites

- Python 3.14+
- Node.js 22+
- npm 10+
- A Walrus testnet aggregator URL
- An OpenAI API key

### Backend Setup

```bash
# Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your values:
#   OPENAI_API_KEY=sk-...
#   WALRUS_AGGREGATOR=https://aggregator.walrus-testnet.example.com
#   WALRUS_PUBLISHER=https://publisher.walrus-testnet.example.com
#   CORS_ORIGIN=http://localhost:5173

# Run the server
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs at `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

### Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

All 13 tests pass with no external dependencies. Test coverage includes health checks, statement submission (new topic, consistent, contradictory, empty, too long), history retrieval (empty user, chronological order), contradiction counts (empty, multi-topic), resilience (Walrus failure, concurrent user isolation, exact quote verification).

---

## API Reference

### `GET /api/health`

Returns server status and dependency health.

```json
{
  "status": "ok",
  "walrus_reachable": true,
  "openai_configured": true
}
```

### `POST /api/statement`

Submit a user statement for processing.

**Request:**
```json
{
  "user_id": "alice",
  "statement": "Brazil will win the World Cup"
}
```

**Response (new topic, no contradiction):**
```json
{
  "reply": "Brazil are always strong contenders...",
  "contradiction_detected": false,
  "contradiction": null,
  "blob_id": "test_blob_3"
}
```

**Response (contradiction detected):**
```json
{
  "reply": "You said earlier that Brazil would struggle...",
  "contradiction_detected": true,
  "contradiction": {
    "topic": "Brazil",
    "previous_statement": "Brazil will struggle this tournament",
    "current_statement": "Brazil is the best team here",
    "previous_stance": "negative",
    "current_stance": "positive"
  },
  "blob_id": "test_blob_5"
}
```

### `GET /api/history/{user_id}`

Returns chronological opinion history for a user.

```json
{
  "user_id": "alice",
  "opinions": [
    {
      "topic": "Brazil",
      "stance": "positive",
      "statement": "Brazil will win the World Cup",
      "timestamp": "2026-06-17T12:00:00+00:00"
    }
  ],
  "blob_id": "test_blob_3"
}
```

### `GET /api/topic/{user_id}/{topic}`

Returns opinions for a specific topic.

### `GET /api/contradictions/{user_id}`

Returns all contradiction events for a user.

```json
{
  "user_id": "alice",
  "contradictions": [
    {
      "topic": "Brazil",
      "previous_statement": "Brazil will struggle this tournament",
      "current_statement": "Brazil is the best team here",
      "previous_stance": "negative",
      "current_stance": "positive",
      "detected_at": "2026-06-17T12:05:00+00:00"
    }
  ],
  "contradiction_count": 1
}
```

---

## Environment Variables

| Variable            | Required | Default          | Description                              |
|---------------------|----------|------------------|------------------------------------------|
| `OPENAI_API_KEY`    | Yes      | --               | OpenAI API key for structured outputs    |
| `WALRUS_AGGREGATOR` | Yes      | --               | Walrus aggregator URL for reading blobs  |
| `WALRUS_PUBLISHER`  | Yes      | --               | Walrus publisher URL for storing blobs   |
| `CORS_ORIGIN`       | No       | `http://localhost:5173` | Allowed CORS origin               |
| `DATABASE_URL`      | No       | `sqlite:///hottake.db`  | SQLite database path             |

---

## Design System

The frontend uses a dark, minimal aesthetic inspired by monitoring dashboards and terminal UIs.

- Background: `#09090B`
- Surface: `#18181B`
- Accent (contradiction alert): `#EF4444` (red)
- Accent (information): `#6366F1` (indigo)
- Typography: system-ui stack
- Animation: Framer Motion (scale+fade for contradictions, slide-in for receipts panel, pulse for skeletons, typing effect for AI replies)
- Error boundaries: every data-dependent component has explicit loading, error, and empty states

No gradients, no glassmorphism, no pill buttons, no emoji.

---

## Testing Philosophy

Tests are hermetic by design:

- **In-memory Walrus store** -- A `dict` replaces the network call to Walrus. Store and read operations round-trip through the same dictionary.
- **In-memory SQLite** -- `check_same_thread=False` connection bound to `:memory:`. No files are created or cleaned up.
- **Mocked OpenAI** -- `extract_topic` returns deterministic `(topic, stance)` tuples from a configurable sequence.
- **Patched agent methods** -- `get_user_memory` and `save_user_memory` are patched at the `agent` module level to use the in-memory store instead of the real `memory_store` functions.
- **Isolation** -- Every test gets a fresh in-memory store, fresh SQLite connection, and reset global state.

The result: 13 tests that execute in under 4 seconds with zero external dependencies.

---

## License

MIT
