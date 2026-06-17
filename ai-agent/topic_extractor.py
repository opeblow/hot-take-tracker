from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from prompts import TOPIC_EXTRACTION_SYSTEM_PROMPT, TOPIC_EXTRACTION_SCHEMA
from exceptions import TopicExtractionError

logger = logging.getLogger(__name__)

_EXTRACTION_TIMEOUT_S = 3


def extract_topic(
    statement: str,
    client: OpenAI,
    model: str = "gpt-4o-mini",
) -> tuple[str, str]:
    """Extract (topic, stance) from *statement* using OpenAI structured output.

    Raises
    ------
    TopicExtractionError
        If the call times out, returns malformed JSON, or any OpenAI API error
        occurs.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": TOPIC_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": statement},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "topic_extraction",
                    "schema": TOPIC_EXTRACTION_SCHEMA,
                    "strict": True,
                },
            },
            timeout=_EXTRACTION_TIMEOUT_S,
        )
    except Exception as exc:
        raise TopicExtractionError(statement, str(exc))

    raw: str | None = response.choices[0].message.content
    if not raw:
        raise TopicExtractionError(statement, "empty response from OpenAI")

    try:
        parsed: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TopicExtractionError(statement, f"malformed JSON: {exc}")

    topic: str | None = parsed.get("topic")
    stance: str | None = parsed.get("stance")

    if not topic or not stance or stance not in ("positive", "negative", "neutral"):
        raise TopicExtractionError(
            statement,
            f"invalid extracted data: topic={topic!r}, stance={stance!r}",
        )

    logger.debug("Extracted topic=%s stance=%s from statement", topic, stance)
    return topic, stance
