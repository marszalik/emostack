import uuid

from emostack.core.promptTemplate import promptTemplate
from emostack.emoThought.Author import Author
from emostack.emoThought.Origin import Origin


class CognitiveConstruct:
    """What the being thought about itself, in reflection: not lived, so it has no episodes. It
    has the form of an emo-thought and a text of its own. It never enters the felt state; it lives
    in the accessibility slot and is protected from sleep."""

    kind = None
    slotRole = None

    def __init__(self, id, beingId, text, feeling, conclusion, valence, strength, happenedAt,
                 vector=None):
        self.id = id
        self.beingId = beingId
        self.text = text
        self.feeling = feeling
        self.conclusion = conclusion
        self.valence = float(valence)
        self.strength = strength
        self.happenedAt = float(happenedAt)
        self.vector = list(vector or [])
        self.author = Author.itself()
        self.origin = Origin.LIVED
        self.episodes = []
        self.hitEpisode = None

    @staticmethod
    def newId():
        return f"rec-{uuid.uuid4().hex[:12]}"

    @property
    def intensity(self):
        return self.strength.intensity

    @property
    def lastFelt(self):
        return self.strength.lastFelt

    def isConstruct(self):
        return True

    def isGiven(self):
        return False

    def sameSign(self, valence):
        return (self.valence >= 0) == (valence >= 0)

    def feltAt(self, now, law):
        return self.strength.feltAt(now, self.valence, law)

    def statement(self):
        """The construct as the being holds it: 'I decided: …'."""
        words = promptTemplate.beside(__file__, "construct.prompt")
        return words.fill("statement", PREFIX=words.text(self.kind), TEXT=self.text)

    def embeddingText(self):
        return f"{self.statement()}\n{self.conclusion}".strip()
