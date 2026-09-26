class TurnOutcome:
    """What a trigger produced that the world can see or the application may show: the words the
    being said (empty for silence) and the thoughts it formed on the way."""

    def __init__(self, words="", thoughts=None, failed=False):
        self.words = words
        self.thoughts = list(thoughts or [])
        self.failed = failed
