from emostack.action.Action import Action
from emostack.action.ActionTarget import ActionTarget


class SearchMemory(Action):
    """The being reaches into its memory for what it names."""
    target = ActionTarget.MEMORY
    replyNames = ("search",)
    reflectionNames = ("search_more",)

    def __init__(self, query):
        self.query = query

    def execute(self, performer):
        return performer.performSearchMemory(self)
