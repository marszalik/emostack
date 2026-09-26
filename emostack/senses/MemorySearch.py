class MemorySearch:
    """One search the being made in its memory this turn, and what it brought: events found, and
    the being's own later thoughts about the theme when only those came up."""

    def __init__(self, query, found, ownThoughtsOnly=0):
        self.query = query
        self.found = found
        self.ownThoughtsOnly = ownThoughtsOnly
