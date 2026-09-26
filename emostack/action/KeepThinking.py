from emostack.action.Action import Action
from emostack.action.ActionTarget import ActionTarget


class KeepThinking(Action):
    """In reflection: think once more, in the direction named."""
    target = ActionTarget.SELF
    reflectionNames = ("keep_thinking",)

    def __init__(self, direction=""):
        self.direction = direction

    def execute(self, performer):
        return performer.performKeepThinking(self)
