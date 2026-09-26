import threading
import time
import uuid


class LiveConversation:
    """A conversation open in someone's browser: whose it is, with which being, the engine it runs
    on, what has been said so far, and the calls behind each message (shown to administrators)."""

    def __init__(self, owner, level, beingId, beingName, person, engine):
        self.id = uuid.uuid4().hex[:12]
        self.owner = owner
        self.level = level
        self.beingId = beingId
        self.beingName = beingName
        self.person = person
        self.engine = engine
        self.conversation = None
        self.messages = []
        self.busy = False
        self.closed = False
        self.lock = threading.Lock()
        self.calls = []
        self.lastActivity = time.time()
        engine.processor.addRecorder(self.calls.append)

    def takeCalls(self):
        calls, self.calls[:] = list(self.calls), []
        return calls if self.level >= 3 else []

    def add(self, role, text, **values):
        message = dict(values, role=role, text=text, at=time.time())
        self.messages.append(message)
        self.lastActivity = time.time()
        return message
