import uuid

from emostack.emoThought.Author import Author
from emostack.emoThought.Origin import Origin
from emostack.emoThought.Strength import Strength


class EmoThought:
    """A felt interpretation of what happened: the feeling in words, the conclusion drawn, how
    pleasant it was and how strong. It has no event of its own; its events are its episodes.
    Its valence is never rewritten; only its strength changes, and when it was last felt."""

    def __init__(self, id, beingId, author, feeling, conclusion, valence, strength, happenedAt,
                 origin=Origin.LIVED, vector=None, originEpisodeId=""):
        self.id = id
        self.beingId = beingId
        self.author = author
        self.feeling = feeling
        self.conclusion = conclusion
        self.valence = float(valence)
        self.strength = strength
        self.happenedAt = float(happenedAt)
        self.origin = origin
        self.vector = list(vector or [])
        self.originEpisodeId = originEpisodeId
        self.episodes = None
        self.hitEpisode = None

    @staticmethod
    def newId():
        return f"rec-{uuid.uuid4().hex[:12]}"

    @classmethod
    def lived(cls, beingId, person, feeling, conclusion, valence, intensity, at):
        return cls(cls.newId(), beingId, Author.person(person), feeling, conclusion, valence,
                   Strength(intensity, at), at)

    @property
    def intensity(self):
        return self.strength.intensity

    @property
    def lastFelt(self):
        return self.strength.lastFelt

    def isConstruct(self):
        return False

    def isGiven(self):
        return self.origin is Origin.GIVEN

    def isNegative(self):
        return self.valence < 0

    def sameSign(self, valence):
        return (self.valence >= 0) == (valence >= 0)

    def feltAt(self, now, law):
        return self.strength.feltAt(now, self.valence, law)

    def embeddingText(self):
        """The meaning of the record; the event's own vector sits on its episode."""
        return (self.conclusion or "").strip()
