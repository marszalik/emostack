from enum import Enum


class SlotRole(Enum):
    """ACT: what the being acts on or reaches for (decision, goal, dream); it has the reserved
    place in the accessibility slot. HELD_BY_STRENGTH: beliefs and thoughts, which compete for
    the free places by intensity."""
    ACT = "act"
    HELD_BY_STRENGTH = "heldByStrength"
