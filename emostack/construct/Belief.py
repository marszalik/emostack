from emostack.construct.CognitiveConstruct import CognitiveConstruct
from emostack.construct.SlotRole import SlotRole


class Belief(CognitiveConstruct):
    """What the being holds true of how things, people or it itself are."""
    kind = "belief"
    slotRole = SlotRole.HELD_BY_STRENGTH
