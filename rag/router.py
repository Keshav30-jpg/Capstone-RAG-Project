# Decides what to do with an incoming user message BEFORE any expensive work happens.

import re
from enum import Enum


GREETING_PATTERNS = {
    "hi", "hello", "hey", "hiya", "yo",
    "good morning", "good afternoon", "good evening",
    "thanks", "thank you", "thx", "ty",
    "how are you", "how's it going", "whats up", "what's up", "sup",
    "bye", "goodbye", "see you", "ok", "okay", "cool", "nice", "great",
}


class RouteType(str, Enum):
    GREETING = "greeting"
    NO_PDF = "no_pdf"
    RAG = "rag"


def _normalize(message: str) -> str:
    """Lowercase, strip, and remove punctuation so pattern matching is forgiving."""
    text = message.lower().strip()
    text = re.sub(r"[^\w\s']", "", text)  
    return text


def _is_greeting(message: str) -> bool:
    
    normalized = _normalize(message)
    if normalized in GREETING_PATTERNS:
        return True
    words = normalized.split()
    if len(words) <= 3 and any(words[0] == g.split()[0] for g in GREETING_PATTERNS if g.split()):
        # First word matches a known greeting's first word, and message is short.
        return normalized.split()[0] in {g.split()[0] for g in GREETING_PATTERNS}
    return False


def route_message(message: str, has_pdf: bool) -> RouteType:
    """
    Decide how to handle an incoming message.

    """
    if _is_greeting(message):
        return RouteType.GREETING

    if not has_pdf:
        return RouteType.NO_PDF

    return RouteType.RAG