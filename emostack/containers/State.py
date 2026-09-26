class State:
    """What the being feels now: the most recent records of its life together with the strongest
    associations, ordered by how strongly each is still felt and admitted up to a budget, because
    attention is finite. An association wins over a recent record with the same id: freshly evoked
    counts as felt now."""

    def __init__(self, entries):
        self.entries = list(entries)

    @classmethod
    def compose(cls, recent, associations, now, fading, budget):
        """Returns the state and the associations that did not fit (they go to the focus)."""
        associationIds = {record.id for record in associations}
        pool = list(associations) + [record for record in recent if record.id not in associationIds]
        pool.sort(key=lambda record: record.feltAt(now, fading), reverse=True)
        entries, mass = [], 0.0
        for record in pool:
            felt = record.feltAt(now, fading)
            if not entries or mass + felt <= budget:
                entries.append(record)
                mass += felt
        state = cls(entries)
        stateIds = state.ids()
        return state, [record for record in associations if record.id not in stateIds]

    def ids(self):
        return {record.id for record in self.entries}

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)
