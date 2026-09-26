from emostack.construct.Belief import Belief
from emostack.construct.Decision import Decision
from emostack.construct.Dream import Dream
from emostack.construct.Goal import Goal
from emostack.construct.Thought import Thought


class constructFactory:
    """A kind of construct → its class."""

    kinds = {cls.kind: cls for cls in (Thought, Belief, Decision, Goal, Dream)}

    def classOf(self, kind):
        return self.kinds[kind]

    def isKind(self, kind):
        return kind in self.kinds

    def create(self, kind, **fields):
        return self.kinds[kind](**fields)
