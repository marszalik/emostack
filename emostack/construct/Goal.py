from emostack.construct.CognitiveConstruct import CognitiveConstruct
from emostack.construct.SlotRole import SlotRole


class Goal(CognitiveConstruct):
    """What the being is working toward."""
    kind = "goal"
    slotRole = SlotRole.ACT
