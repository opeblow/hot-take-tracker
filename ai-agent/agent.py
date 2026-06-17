from __future__ import annotations

import logging
import time
from typing import Any, Optional

from openai import OpenAI

from models import AgentResponse, ContradictionEvent, Opinion, UserMemory
from prompts import SYSTEM_PROMPT_WITH_CONTRADICTION, SYSTEM_PROMPT_NO_CONTRADICTION
from memory_store import get_user_memory, save_user_memory
from topic_extractor import extract_topic
from contradiction import find_contradiction
from exceptions import (
    MemoryPersistenceWarning,
    TopicExtractionError,
    WalrusStoreError,
    WalrusTimeoutError,
)

logger = logging.getLogger(__name__)

_REPLY_MODEL = "gpt-4o-mini"
_CONFIDENCE_EXACT_MATCH = 1.0


class HotTakeAgent:
    """The central agent that orchestrates memory, topic extraction,
    contradiction detection, and reply generation."""

    def __init__(
        self,
        openai_client: OpenAI,
        blob_registry: dict[str, str],
        publisher_url: str,
        aggregator_url: str,
    ) -> None:
        self.client = openai_client
        self.registry = blob_registry
        self.publisher_url = publisher_url
        self.aggregator_url = aggregator_url

    # ------------------------------------------------------------------
    def process_statement(self, user_id: str, statement: str) -> AgentResponse:
        """Run the full Hot Take Tracker pipeline on *statement*.

        Returns
        -------
        AgentResponse
            The agent's reply, detection results, and the new opinion.
        """
        timings: dict[str, float] = {}

        # --- 1. Load memory ---------------------------------------------------
        t0 = time.perf_counter()
        memory: UserMemory
        try:
            memory = get_user_memory(user_id, self.registry, self.aggregator_url)
        except Exception as exc:
            logger.error("Unexpected error loading memory for '%s': %s", user_id, exc)
            memory = UserMemory(user_id=user_id)
        timings["load_memory"] = time.perf_counter() - t0

        # --- 2. Extract topic & stance ----------------------------------------
        t0 = time.perf_counter()
        try:
            topic, stance = extract_topic(statement, self.client)
        except TopicExtractionError as exc:
            logger.error("Topic extraction failed: %s", exc)
            raise
        timings["extract_topic"] = time.perf_counter() - t0

        # --- 3. Contradiction check -------------------------------------------
        t0 = time.perf_counter()
        contradicted: Optional[Opinion] = find_contradiction(
            topic, stance, memory.opinions
        )
        timings["contradiction_check"] = time.perf_counter() - t0

        contradiction_detected = contradicted is not None

        # --- 4. Build new Opinion ---------------------------------------------
        new_opinion = Opinion(
            user_id=user_id,
            topic=topic,
            statement=statement,
            stance=stance,
        )

        if contradicted is not None:
            event = ContradictionEvent(
                old_opinion=contradicted,
                new_opinion=new_opinion,
            )
            memory.contradictions.append(event)
            logger.info(
                "Contradiction event recorded for user '%s' on topic '%s'",
                user_id,
                topic,
            )

        # --- 5. Generate reply ------------------------------------------------
        t0 = time.perf_counter()
        reply = self._generate_reply(statement, contradicted)
        timings["generate_reply"] = time.perf_counter() - t0

        # --- 6. Append to history & save --------------------------------------
        t0 = time.perf_counter()
        memory.opinions.append(new_opinion)
        try:
            new_blob_id = save_user_memory(memory, self.publisher_url)
            memory.blob_id = new_blob_id
            self.registry[user_id] = new_blob_id
            logger.info("Updated registry for user '%s' -> blob %s", user_id, new_blob_id)
        except (WalrusStoreError, WalrusTimeoutError) as exc:
            self._flag_persistence_failure(user_id, exc)
        except Exception as exc:
            self._flag_persistence_failure(user_id, exc)
        timings["save_memory"] = time.perf_counter() - t0

        # --- Log timings ------------------------------------------------------
        total = sum(timings.values())
        logger.info(
            "Request for user '%s' completed in %.2fs: %s",
            user_id,
            total,
            {k: f"{v:.3f}s" for k, v in timings.items()},
        )

        return AgentResponse(
            reply=reply,
            contradiction_detected=contradiction_detected,
            contradicted_opinion=contradicted,
            new_opinion=new_opinion,
            confidence=_CONFIDENCE_EXACT_MATCH,
        )

    # ------------------------------------------------------------------
    def _generate_reply(
        self,
        statement: str,
        contradicted: Optional[Opinion],
    ) -> str:
        """Call the LLM with the appropriate system prompt and return the reply text."""
        if contradicted is not None:
            system = SYSTEM_PROMPT_WITH_CONTRADICTION
            user_prompt = (
                f"User's new statement: {statement}\n"
                f"Their past statement on the same topic: \"{contradicted.statement}\"\n"
                f"Date of that past statement: {contradicted.timestamp}"
            )
        else:
            system = SYSTEM_PROMPT_NO_CONTRADICTION
            user_prompt = statement

        try:
            response = self.client.chat.completions.create(
                model=_REPLY_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_prompt},
                ],
                timeout=10,
            )
        except Exception as exc:
            logger.error("Reply generation failed: %s", exc)
            return (
                "I ran into a hiccup generating my response, but I've noted your take! "
                "I'll remember this one."
            )

        content: str | None = response.choices[0].message.content
        return content or "Got it — I'll remember that take!"

    # ------------------------------------------------------------------
    @staticmethod
    def _flag_persistence_failure(user_id: str, exc: Exception) -> None:
        """Log persistence failures clearly so they're caught pre-demo."""
        logger.error(
            "MEMORY NOT PERSISTED for user '%s'. This turn's opinion is lost "
            "if the process restarts. Error: %s",
            user_id,
            exc,
        )
