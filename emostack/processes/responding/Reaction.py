class Reaction:
    """What the reply call returned: this moment as the being felt it, the retelling of the exchange,
    the words it would say, and the act it chose."""

    def __init__(self, feeling, conclusion, valence, intensity, retold, words, action,
                 failed=False):
        self.feeling = feeling
        self.conclusion = conclusion
        self.valence = valence
        self.intensity = intensity
        self.retold = retold
        self.words = words
        self.action = action
        self.failed = failed

    @classmethod
    def failure(cls):
        return cls("", "", 0.0, 0.0, "", "", None, failed=True)
