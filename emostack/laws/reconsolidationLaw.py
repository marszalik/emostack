class reconsolidationLaw:
    """A recurrence brings a memory back toward what is felt now, closing a share of the gap, and
    never past it. The valence is never touched: comfort does not turn a loss into a pleasure, it
    stands beside it as a record of its own."""

    def __init__(self, closing=0.6):
        self.closing = float(closing)

    def restored(self, current, feltNow):
        if feltNow > current:
            return current + (feltNow - current) * self.closing
        return current
