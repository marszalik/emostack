class Disposition:
    """How the being meets a kind of situation: a learned rule 'when this happens → this is what
    I do', with a signed weight. Negative when it was learned from what hurt. Never felt, never
    seen by introspection; it acts while a reply is composed."""

    activeThreshold = 0.05

    def __init__(self, id, beingId, rule, weight, count=1, updatedAt=0.0):
        self.id = id
        self.beingId = beingId
        self.rule = rule
        self.weight = float(weight)
        self.count = int(count)
        self.updatedAt = float(updatedAt)

    def isActive(self):
        return abs(self.weight) > self.activeThreshold
