from __future__ import annotations

from typing import Optional

from models import Opinion

_STANCE_OPPOSITES: dict[str, str] = {
    "positive": "negative",
    "negative": "positive",
}


def _topics_match(a: str, b: str) -> bool:
    """Case-insensitive fuzzy topic comparison."""
    return a.strip().lower() == b.strip().lower()


def find_contradiction(
    new_topic: str,
    new_stance: str,
    history: list[Opinion],
) -> Optional[Opinion]:
    """Search *history* for an ``Opinion`` on the same topic with the opposite stance.

    Returns the *most recent* contradicting ``Opinion``, or ``None`` when no
    contradiction exists.

    This function is **deterministic**: same inputs always return the same
    output.  No randomness, no LLM calls — pure logic only.
    """
    opposite_stance = _STANCE_OPPOSITES.get(new_stance)
    if opposite_stance is None:
        return None

    candidate: Optional[Opinion] = None
    for opinion in history:
        if _topics_match(opinion.topic, new_topic) and opinion.stance == opposite_stance:
            if candidate is None or opinion.timestamp > candidate.timestamp:
                candidate = opinion

    return candidate
