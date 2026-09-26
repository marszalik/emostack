class Encoding:
    """Where a moment went: the record it now belongs to, the episode that carries it, whether that
    record is new, and the record whose strength it restores, if any."""

    def __init__(self, record, episode, restores=None, isNew=True):
        self.record = record
        self.episode = episode
        self.restores = restores
        self.isNew = isNew
