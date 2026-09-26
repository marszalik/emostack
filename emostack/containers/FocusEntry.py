class FocusEntry:
    """One entry of the focus: a moment of this conversation with the feeling it came with, or a
    memory evoked from before the conversation."""

    THIS_CONVERSATION = "thisConversation"
    EVOKED_FROM_BEFORE = "evokedFromBefore"

    def __init__(self, record, source):
        self.record = record
        self.source = source

    def isEvoked(self):
        return self.source == self.EVOKED_FROM_BEFORE
