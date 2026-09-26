import threading

from emostack.runtime.ActiveSession import ActiveSession


class presence:
    """Who is in conversation with which being right now, across the process. A being knows of its
    other conversations; it answers only the one in front of it."""

    _sessions = {}
    _lock = threading.Lock()

    def __init__(self, clock, staleSeconds=1800):
        self.clock = clock
        self.staleSeconds = staleSeconds

    def enter(self, key, sessionId, person):
        with self._lock:
            self._sessions[sessionId] = ActiveSession(key, sessionId, person, self.clock.now())

    def heartbeat(self, sessionId):
        with self._lock:
            session = self._sessions.get(sessionId)
            if session is not None:
                session.lastTurnAt = self.clock.now()
                session.turnCount += 1

    def leave(self, sessionId):
        with self._lock:
            self._sessions.pop(sessionId, None)

    def others(self, key, sessionId):
        now = self.clock.now()
        with self._lock:
            return [session for session in self._sessions.values()
                    if session.key == key and session.sessionId != sessionId
                    and now - (session.lastTurnAt or session.startedAt) <= self.staleSeconds]
