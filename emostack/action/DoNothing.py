from emostack.action.Action import Action
from emostack.action.ActionTarget import ActionTarget


class DoNothing(Action):
    """In reflection: just a thought; nothing follows."""
    target = ActionTarget.SELF
    reflectionNames = ("none",)

    def execute(self, performer):
        return performer.performDoNothing(self)
