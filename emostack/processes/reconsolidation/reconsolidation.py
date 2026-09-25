class reconsolidation:
    """A memory felt again comes back toward what is felt now, never past it. Its valence is never
    rewritten; its date stays the date of what happened; only its strength and when it was last felt
    change."""

    def __init__(self, hippocampus, fading, law, clock):
        self.hippocampus = hippocampus
        self.fading = fading
        self.law = law
        self.clock = clock

    def restore(self, record, feltNow):
        current = self.fading.settle(record)
        self.hippocampus.setStrength(record, self.law.restored(current, float(feltNow)), self.clock.now())
