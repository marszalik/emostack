import math

from emostack.construct.Thought import Thought
from emostack.emoThought.Strength import Strength


class constructFormation:
    """Keeps what a reflection formed as the being's own record. A thought almost the same as one
    the being already had is that thought recurring: nothing new is written and the old one is
    returned, to be restored. A construct almost the same as one of its kind is strengthened
    instead of written twice."""

    def __init__(self, hippocampus, embedder, constructs, clock, duplicate=0.90, reinforcement=0.1):
        self.hippocampus = hippocampus
        self.embedder = embedder
        self.constructs = constructs
        self.clock = clock
        self.duplicate = duplicate
        self.reinforcement = reinforcement

    def keepThought(self, beingId, step):
        """Returns (thought, isRecurrence)."""
        thought = self._new(Thought, beingId, step.thought, step)
        same = self._same(thought)
        if same is not None:
            return same, True
        self.hippocampus.keep(thought)
        return thought, False

    def keepConstruct(self, beingId, kind, text, step):
        construct = self._new(self.constructs.classOf(kind), beingId, text, step)
        same = self._same(construct)
        if same is not None:
            self.hippocampus.setStrength(same, min(1.0, same.intensity + self.reinforcement), self.clock.now())
            return same
        self.hippocampus.keep(construct)
        return construct

    def _new(self, cls, beingId, text, step):
        now = self.clock.now()
        construct = cls(id=cls.newId(), beingId=beingId, text=text, feeling=step.feeling,
                        conclusion=step.conclusion, valence=step.valence,
                        strength=Strength(step.intensity, now), happenedAt=now)
        construct.vector = self.embedder.embed(construct.embeddingText())
        return construct

    def _same(self, construct):
        for other in self.hippocampus.constructsOfKind(construct.kind):
            if (other.vector and len(other.vector) == len(construct.vector)
                    and self._cosine(other.vector, construct.vector) >= self.duplicate):
                return other
        return None

    @staticmethod
    def _cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        normA = math.sqrt(sum(x * x for x in a))
        normB = math.sqrt(sum(y * y for y in b))
        return dot / (normA * normB) if normA and normB else 0.0
