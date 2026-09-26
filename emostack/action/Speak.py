from emostack.action.Action import Action
from emostack.action.ActionTarget import ActionTarget


class Speak(Action):
    target = ActionTarget.WORLD

    def __init__(self, words):
        self.words = words

    def execute(self, performer):
        return performer.performSpeak(self)
