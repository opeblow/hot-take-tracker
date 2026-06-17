from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from models import ContradictionEvent, Opinion, UserMemory
from exceptions import WalrusStoreError, WalrusReadError, WalrusTimeoutError

logger = logging.getLogger(__name__)

_WALRUS_STORE_TIMEOUT = 10
_WALRUS_READ_TIMEOUT = 10


def store_memory(
    data: dict[str, Any],
    publisher_url: str,
) -> str:
    """PUT *data* as JSON to the Walrus publisher and return the *blob_id*.

    Raises
    ------
    WalrusStoreError
        On any non-2xx HTTP response, including the status and body.
    WalrusTimeoutError
        If the request exceeds the 10-second timeout.
    """
    url = f"{publisher_url.rstrip('/')}/v1/blobs?epochs=10"

    try:
        response = httpx.put(
            url,
            content=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=_WALRUS_STORE_TIMEOUT,
        )
    except httpx.TimeoutException:
        raise WalrusTimeoutError("store", _WALRUS_STORE_TIMEOUT)

    if not response.is_success:
        raise WalrusStoreError(response.status_code, response.text)

    try:
        result: dict[str, Any] = response.json()
        blob_id: str = result["blobId"]
    except (KeyError, json.JSONDecodeError) as exc:
        raise WalrusStoreError(
            response.status_code,
            f"unexpected response format: {response.text}",
        ) from exc

    logger.info("Stored blob %s (%d bytes)", blob_id, len(json.dumps(data)))
    return blob_id


def read_memory(blob_id: str, aggregator_url: str) -> dict[str, Any]:
    """GET *blob_id* from the Walrus aggregator and return parsed JSON.

    Raises
    ------
    WalrusReadError
        If the blob_id is invalid, the HTTP call fails, or the response body
        is not valid JSON.
    WalrusTimeoutError
        If the request exceeds the 10-second timeout.
    """
    url = f"{aggregator_url.rstrip('/')}/v1/blobs/{blob_id}"

    try:
        response = httpx.get(url, timeout=_WALRUS_READ_TIMEOUT)
    except httpx.TimeoutException:
        raise WalrusTimeoutError("read", _WALRUS_READ_TIMEOUT)

    if not response.is_success:
        raise WalrusReadError(
            blob_id,
            f"HTTP {response.status_code}: {response.text}",
        )

    try:
        data: dict[str, Any] = response.json()
    except json.JSONDecodeError as exc:
        raise WalrusReadError(
            blob_id,
            f"invalid JSON: {exc}",
        ) from exc

    return data


def get_user_memory(
    user_id: str,
    blob_registry: dict[str, str],
    aggregator_url: str,
) -> UserMemory:
    """Resolve *user_id* from *blob_registry* and return a ``UserMemory``.

    If the user has no entry in the registry, or the stored blob cannot be
    read, a fresh empty ``UserMemory`` is returned so the conversation can
    continue uninterrupted.
    """
    blob_id = blob_registry.get(user_id)

    if blob_id is None:
        logger.info("No blob_id for user '%s', returning fresh memory", user_id)
        return UserMemory(user_id=user_id, opinions=[], blob_id=None)

    try:
        raw = read_memory(blob_id, aggregator_url)
    except (WalrusReadError, WalrusTimeoutError) as exc:
        logger.warning(
            "Could not read blob '%s' for user '%s': %s. Returning empty memory.",
            blob_id,
            user_id,
            exc,
        )
        return UserMemory(user_id=user_id, opinions=[], blob_id=blob_id)

    try:
        opinions = [Opinion(**o) for o in raw.get("opinions", [])]
    except (ValueError, TypeError) as exc:
        logger.warning(
            "Malformed opinion data in blob '%s' for user '%s': %s. Returning empty memory.",
            blob_id,
            user_id,
            exc,
        )
        return UserMemory(user_id=user_id, opinions=[], blob_id=blob_id)

    try:
        contradictions = [
            ContradictionEvent(**c) for c in raw.get("contradictions", [])
        ]
    except (ValueError, TypeError) as exc:
        logger.warning(
            "Malformed contradiction data in blob '%s' for user '%s': %s. Skipping contradictions.",
            blob_id,
            user_id,
            exc,
        )
        contradictions = []

    logger.info("Loaded %d opinions for user '%s'", len(opinions), user_id)
    return UserMemory(
        user_id=user_id,
        opinions=opinions,
        contradictions=contradictions,
        blob_id=blob_id,
    )


def save_user_memory(
    memory: UserMemory,
    publisher_url: str,
) -> str:
    """Serialize *memory* to JSON, store it via ``store_memory``, and return the new blob_id.

    Raises
    ------
    WalrusStoreError
    WalrusTimeoutError
    """
    data = memory.model_dump(mode="json")
    blob_id = store_memory(data, publisher_url)
    logger.info("Saved %d opinions for user '%s' to blob %s", len(memory.opinions), memory.user_id, blob_id)
    return blob_id
