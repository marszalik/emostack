from emostack.action.Action import Action
from emostack.action.ActionTarget import ActionTarget


class Think(Action):
    """The being stops to think before it answers: a reflection runs first."""
    target = ActionTarget.SELF
    replyNames = ("introspect",)

    def __init__(self, angle=""):
        self.angle = angle

    def execute(self, performer):
        return performer.performThink(self)
