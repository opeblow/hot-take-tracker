import logging
import sys

from agent import HotTakeAgent
from models import AgentResponse, Opinion, UserMemory

logging.getLogger(__name__).addHandler(logging.NullHandler())


def setup_logging(level: int = logging.INFO) -> None:
    """Configure structured logging for the ai-agent package.

    Call once at application startup (e.g. from ``main``) to enable
    consistent log output across all modules.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root = logging.getLogger(__name__)
    root.setLevel(level)
    root.addHandler(handler)

__all__ = [
    "AgentResponse",
    "HotTakeAgent",
    "Opinion",
    "UserMemory",
    "setup_logging",
]
