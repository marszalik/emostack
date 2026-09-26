from emostack.trigger.Trigger import Trigger


class Utterance(Trigger):
    """Someone says something. It gets a reply."""

    def __init__(self, person, words, at):
        super().__init__(person, at)
        self.words = words

    def enter(self, handler):
        return handler.onUtterance(self)
