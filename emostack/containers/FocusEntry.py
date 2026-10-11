class FocusEntry:
    """One entry of the focus line: a feeling the being brought into the conversation from before, a
    moment of this conversation with the feeling it came with, a memory evoked during it, or one of the
    being's own thoughts held in mind. `at` is when the entry came into view, which is its place in the
    line."""

    CARRIED_FROM_BEFORE = "carriedFromBefore"
    THIS_CONVERSATION = "thisConversation"
    EVOKED_FROM_BEFORE = "evokedFromBefore"
    HELD_THOUGHT = "heldThought"

    def __init__(self, record, source, at=0.0):
        self.record = record
        self.source = source
        self.at = at
        self.folded = False

    def isEvoked(self):
        return self.source == self.EVOKED_FROM_BEFORE

    def isCarried(self):
        return self.source == self.CARRIED_FROM_BEFORE

    def isHeldThought(self):
        return self.source == self.HELD_THOUGHT

    def isMoment(self):
        return self.source == self.THIS_CONVERSATION

    def isFromBefore(self):
        """Evoked or carried: an event of the past, shown retold."""
        return self.isEvoked() or self.isCarried()
