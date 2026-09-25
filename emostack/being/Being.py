from emostack.being.Temperament import Temperament
from emostack.being.Wakefulness import Wakefulness


class Being:
    """The cognitive construction: its records, containers and processes running over a
    processor. Not the LLM model. It is awake or asleep; while awake, silence leads to a
    reflection and long silence to sleep."""

    def __init__(self, id, name, temperament=None, createdAt=0.0, wakefulness=Wakefulness.ASLEEP,
                 lastActivity=0.0, introspectedIdle=False, wakePending=False, wokeAt=0.0,
                 sleptAt=0.0, consolidated=True):
        self.id = id
        self.name = name
        self.temperament = temperament or Temperament()
        self.createdAt = createdAt
        self.wakefulness = wakefulness
        self.lastActivity = lastActivity
        self.introspectedIdle = introspectedIdle
        self.wakePending = wakePending
        self.wokeAt = wokeAt
        self.sleptAt = sleptAt
        self.consolidated = consolidated

    def isAwake(self):
        return self.wakefulness is Wakefulness.AWAKE

    def wake(self, now):
        """Activity keeps the being awake. Waking from sleep starts a new awake period and asks for
        one reflection first thing."""
        if not self.isAwake():
            self.wakefulness = Wakefulness.AWAKE
            self.wakePending = True
            self.wokeAt = now
            self.consolidated = False
        self.lastActivity = now
        self.introspectedIdle = False

    def fallAsleep(self, now):
        self.wakefulness = Wakefulness.ASLEEP
        self.sleptAt = now
