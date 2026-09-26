class fading:
    """Fading is a process of time: a record's strength falls with the time since it was last felt.
    The fall is read through the fading law and written into the record only when it is next felt,
    so that a recurrence has something to restore."""

    def __init__(self, hippocampus, law, clock):
        self.hippocampus = hippocampus
        self.law = law
        self.clock = clock

    def settle(self, record):
        """Writes the fall since the record was last felt. Returns its strength now."""
        now = self.clock.now()
        felt = record.feltAt(now, self.law)
        self.hippocampus.setStrength(record, felt, now)
        return felt
