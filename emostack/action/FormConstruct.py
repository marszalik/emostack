from emostack.action.Action import Action
from emostack.action.ActionTarget import ActionTarget


class FormConstruct(Action):
    """In reflection: the thought becomes a belief, a decision, a goal or a dream. It ends the
    chain; the construct enters the accessibility slot."""
    target = ActionTarget.SELF
    reflectionNames = ("belief", "decision", "goal", "dream")

    def __init__(self, kind, text):
        self.kind = kind
        self.text = text

    def execute(self, performer):
        return performer.performFormConstruct(self)
