from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

_connection: Optional[sqlite3.Connection] = None


def _get_db_path() -> str:
    raw = settings.database_url
    if raw.startswith("sqlite:///"):
        return raw[len("sqlite:///"):]
    return raw


def _get_conn() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        db_path = _get_db_path()
        _connection = sqlite3.connect(
            database=db_path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA journal_mode=WAL")
    return _connection


def init_db() -> None:
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS blob_registry (
            user_id     TEXT PRIMARY KEY,
            blob_id     TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        )
        """
    )
    conn.commit()
    logger.info("Database initialized at %s", _get_db_path())


def get_blob_id(user_id: str) -> Optional[str]:
    conn = _get_conn()
    row = conn.execute(
        "SELECT blob_id FROM blob_registry WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if row is None:
        return None
    return str(row["blob_id"])


def set_blob_id(user_id: str, blob_id: str) -> None:
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT INTO blob_registry (user_id, blob_id, updated_at)
           VALUES (?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET
               blob_id = excluded.blob_id,
               updated_at = excluded.updated_at""",
        (user_id, blob_id, now),
    )
    conn.commit()
