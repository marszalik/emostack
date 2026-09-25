from emostack.construct.CognitiveConstruct import CognitiveConstruct
from emostack.construct.SlotRole import SlotRole


class Thought(CognitiveConstruct):
    """A thought of the being's own, formed in reflection."""
    kind = "thought"
    slotRole = SlotRole.HELD_BY_STRENGTH
