class FilterVerdict:
    """What the association filter answered: which candidates came to mind, whether the words ask
    the being to recall a moment of its own past, and whether they ask what it dreams of,
    believes, has decided or wants."""

    ownKinds = ("dream", "belief", "decision", "goal")

    def __init__(self, kept, asksForMemory=False, asksForOwn=None):
        self.kept = list(kept)
        self.asksForMemory = bool(asksForMemory)
        self.asksForOwn = asksForOwn if asksForOwn in self.ownKinds else None
