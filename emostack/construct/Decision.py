from emostack.construct.CognitiveConstruct import CognitiveConstruct
from emostack.construct.SlotRole import SlotRole


class Decision(CognitiveConstruct):
    """What the being has resolved to do."""
    kind = "decision"
    slotRole = SlotRole.ACT
