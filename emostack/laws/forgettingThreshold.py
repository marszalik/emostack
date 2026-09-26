import math


class forgettingThreshold:
    """The strength a record needs to survive at its age. It rises with age, interpolated in
    log-time between knots (days, intensity); under a day nothing is forgotten. Of old things only
    strong feelings remain."""

    def __init__(self, knots):
        self.knots = sorted((float(days), float(level)) for days, level in knots)

    def at(self, ageDays):
        if not self.knots or ageDays < 1.0:
            return 0.0
        if ageDays <= self.knots[0][0]:
            return self.knots[0][1]
        if ageDays >= self.knots[-1][0]:
            return self.knots[-1][1]
        for (x0, y0), (x1, y1) in zip(self.knots, self.knots[1:]):
            if x0 <= ageDays <= x1:
                share = (math.log(ageDays) - math.log(x0)) / (math.log(x1) - math.log(x0))
                return y0 + share * (y1 - y0)
        return self.knots[-1][1]

    def isTooWeak(self, intensity, ageDays):
        return intensity < self.at(ageDays)
