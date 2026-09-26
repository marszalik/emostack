import uuid

from emostack.episode.Rendering import Rendering


class Episode:
    """One event under an emo-thought, kept as the being will remember it: as it happened, and
    retold in the third person and the past tense. Other people's words and the being's own past
    words live here and nowhere else."""

    def __init__(self, id, beingId, recordId, person, asItHappened, happenedAt, retold="",
                 vector=None):
        self.id = id
        self.beingId = beingId
        self.recordId = recordId
        self.person = person
        self.asItHappened = asItHappened
        self.retold = retold
        self.happenedAt = float(happenedAt)
        self.vector = list(vector or [])

    @staticmethod
    def newId():
        return f"ep-{uuid.uuid4().hex[:12]}"

    def text(self, rendering):
        if rendering is Rendering.RETOLD and (self.retold or "").strip():
            return self.retold.strip()
        return (self.asItHappened or "").strip()
