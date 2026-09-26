class RecallResult:
    """What came to mind for the present words, and what the filter read in them."""

    def __init__(self, records, asksForMemory=False, asksForOwn=None):
        self.records = list(records)
        self.asksForMemory = asksForMemory
        self.asksForOwn = asksForOwn
