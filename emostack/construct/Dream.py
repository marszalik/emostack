from emostack.construct.CognitiveConstruct import CognitiveConstruct
from emostack.construct.SlotRole import SlotRole


class Dream(CognitiveConstruct):
    """What the being wishes for."""
    kind = "dream"
    slotRole = SlotRole.ACT
