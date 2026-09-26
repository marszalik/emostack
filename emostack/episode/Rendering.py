from enum import Enum


class Rendering(Enum):
    """AS_IT_HAPPENED is used for search and for the running conversation; RETOLD, in the third
    person and the past tense, wherever the being reads a memory."""
    AS_IT_HAPPENED = "asItHappened"
    RETOLD = "retold"
