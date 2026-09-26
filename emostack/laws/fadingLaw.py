import math


class fadingLaw:
    """A feeling's strength falls with the time since it was last felt, toward a floor and never
    to zero; negative feelings fall more slowly.

        factor(t) = floor + (1 - floor) · exp(-t / tau)
    """

    day = 86400.0

    def __init__(self, floor=0.3, tauDays=3.0, negativeSlowdown=1.5):
        self.floor = float(floor)
        self.tauDays = float(tauDays)
        self.negativeSlowdown = float(negativeSlowdown)

    def factor(self, ageSeconds, valence):
        if ageSeconds <= 0:
            return 1.0
        tau = self.tauDays * self.day
        if valence < 0:
            tau *= self.negativeSlowdown
        return self.floor + (1.0 - self.floor) * math.exp(-ageSeconds / tau)

    def felt(self, intensity, ageSeconds, valence):
        return max(0.0, min(1.0, float(intensity) * self.factor(ageSeconds, valence)))
