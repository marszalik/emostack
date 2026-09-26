import math


class Temperament:
    """The being's fixed disposition to feel, the same for its whole life.

    valenceBias bends every new feeling toward pleasant or unpleasant, in logit space so that a
    feeling never pins at the pole. intensityAmplification makes the being more (above 1) or less
    (below 1) reactive, as a power so that intensity stays within 0..1. avoidanceWeight is how
    much more a lesson from what hurt weighs than a lesson of the same size from what was good,
    when two learned dispositions collide."""

    def __init__(self, valenceBias=0.0, intensityAmplification=1.0, avoidanceWeight=2.0):
        self.valenceBias = float(valenceBias)
        self.intensityAmplification = float(intensityAmplification)
        self.avoidanceWeight = max(1.0, float(avoidanceWeight))

    @classmethod
    def fromDict(cls, values):
        values = values or {}
        return cls(values.get("valenceBias", 0.0), values.get("intensityAmplification", 1.0),
                   values.get("avoidanceWeight", 2.0))

    def toDict(self):
        return {"valenceBias": self.valenceBias,
                "intensityAmplification": self.intensityAmplification,
                "avoidanceWeight": self.avoidanceWeight}

    def isNeutral(self):
        return self.valenceBias == 0.0 and self.intensityAmplification == 1.0

    def apply(self, valence, intensity):
        """The feeling as this being feels it: (valence, intensity) bent by the temperament."""
        return self.bentValence(valence), self.bentIntensity(intensity)

    def bentValence(self, valence):
        if self.valenceBias == 0.0:
            return max(-1.0, min(1.0, valence))
        valence = max(-0.999, min(0.999, valence))
        return math.tanh(math.atanh(valence) + self.valenceBias)

    def bentIntensity(self, intensity):
        intensity = max(0.0, min(1.0, intensity))
        if self.intensityAmplification <= 0.0:
            return 0.0
        if self.intensityAmplification == 1.0:
            return intensity
        return intensity ** (1.0 / self.intensityAmplification)

    def pull(self, weight):
        """How strongly a disposition of this signed weight pulls: its size, with avoidance
        weighing more."""
        weight = float(weight)
        return abs(weight) * (self.avoidanceWeight if weight < 0 else 1.0)
