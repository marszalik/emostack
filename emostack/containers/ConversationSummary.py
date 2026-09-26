class ConversationSummary:
    """The gist the being keeps of a long talk: what happened and what was said, in its own
    voice, without the emotions. Refreshed every few turns."""

    def __init__(self, everyTurns=3):
        self.everyTurns = everyTurns
        self.text = ""
        self.turns = 0

    def countTurn(self):
        self.turns += 1

    def isDue(self):
        return not self.text or self.turns % max(1, self.everyTurns) == 0
