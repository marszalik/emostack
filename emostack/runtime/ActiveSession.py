class ActiveSession:
    """A conversation in progress, as the other conversations of the same being see it."""

    def __init__(self, key, sessionId, person, startedAt):
        self.key = key
        self.sessionId = sessionId
        self.person = person
        self.startedAt = startedAt
        self.lastTurnAt = 0.0
        self.turnCount = 0
