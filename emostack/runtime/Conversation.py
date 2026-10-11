import uuid

from emostack.containers.Focus import Focus


class Conversation:
    """One conversation of a being with a person, from arrival to departure: its focus, with the
    summary of what has left view, and the record the conversation is currently living."""

    def __init__(self, being, person, startedAt, focusSize=4, focusCap=100, sessionId=None):
        self.being = being
        self.person = person
        self.startedAt = startedAt
        self.sessionId = sessionId or uuid.uuid4().hex[:12]
        self.focus = Focus(focusSize, focusCap)
        self.livingRecordId = None
        self.closingContext = ""
        self.lastAssociations = []
        self.lastDispositions = []
        self.lastHereAndNow = None
        self.closed = False
