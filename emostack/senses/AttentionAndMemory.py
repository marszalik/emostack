class AttentionAndMemory:
    """The being's own channels as counts: how many entries the state holds (or that it is
    withheld), how many memories came to mind, how many records the memory holds, and the
    searches made this turn with their results."""

    def __init__(self, stateCount, associationCount, memoryCount, searches=None, stateWithheld=False):
        self.stateCount = stateCount
        self.associationCount = associationCount
        self.memoryCount = memoryCount
        self.searches = list(searches or [])
        self.stateWithheld = stateWithheld
