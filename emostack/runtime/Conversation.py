import uuid

from emostack.containers.ConversationSummary import ConversationSummary
from emostack.containers.Focus import Focus


class Conversation:
    """One conversation of a being with a person, from arrival to departure: its focus, its
    summary, and the record the conversation is currently living."""

    def __init__(self, being, person, startedAt, focusCap=100, summaryEveryTurns=3, sessionId=None):
        self.being = being
        self.person = person
        self.startedAt = startedAt
        self.sessionId = sessionId or uuid.uuid4().hex[:12]
        self.focus = Focus(focusCap)
        self.summary = ConversationSummary(summaryEveryTurns)
        self.livingRecordId = None
        self.closingContext = ""
        self.lastAssociations = []
        self.closed = False
