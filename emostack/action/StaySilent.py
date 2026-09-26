from emostack.action.Action import Action
from emostack.action.ActionTarget import ActionTarget


class StaySilent(Action):
    """Silence is itself an answer."""
    target = ActionTarget.WORLD

    def execute(self, performer):
        return performer.performStaySilent(self)
