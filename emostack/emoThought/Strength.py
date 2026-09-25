class Strength:
    """How strong a feeling is: its intensity when it was last felt, and when that was. It falls
    with age between the moments it is felt (see fadingLaw); the fall is written into it when it is
    next felt."""

    def __init__(self, intensity, lastFelt):
        self.intensity = float(intensity)
        self.lastFelt = float(lastFelt)

    def feltAt(self, now, valence, law):
        """The strength felt at `now`."""
        return law.felt(self.intensity, now - self.lastFelt, valence)
