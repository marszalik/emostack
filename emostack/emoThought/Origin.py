from enum import Enum


class Origin(Enum):
    """A record is lived, or given at birth by a scenario. A given record is never folded away
    in sleep and never forgotten; otherwise it behaves as lived."""
    LIVED = "lived"
    GIVEN = "given"
