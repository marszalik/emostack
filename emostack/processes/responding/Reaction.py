class Reaction:
    """What the reply call returned: this moment as the being felt it, the retelling of the exchange,
    the entry of the state it re-feels, the words it would say, and the act it chose."""

    def __init__(self, feeling, conclusion, valence, intensity, reinforcesId, retold, words, action,
                 failed=False):
        self.feeling = feeling
        self.conclusion = conclusion
        self.valence = valence
        self.intensity = intensity
        self.reinforcesId = reinforcesId
        self.retold = retold
        self.words = words
        self.action = action
        self.failed = failed

    @classmethod
    def failure(cls):
        return cls("", "", 0.0, 0.0, None, "", "", None, failed=True)
