class ReflectionStep:
    """What one moment of thinking produced: the thought, how it felt, the entry it deepens and
    what follows from it."""

    def __init__(self, thought, feeling, conclusion, valence, intensity, reinforcesId, action):
        self.thought = thought
        self.feeling = feeling
        self.conclusion = conclusion
        self.valence = valence
        self.intensity = intensity
        self.reinforcesId = reinforcesId
        self.action = action
