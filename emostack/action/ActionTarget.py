from enum import Enum


class ActionTarget(Enum):
    """What an act is done to. Only acts on the world are visible to the person."""
    WORLD = "world"
    MEMORY = "memory"
    SELF = "self"
