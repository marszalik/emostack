class Moment:
    """One moment of a conversation, ready to be kept: the event as it happened and retold, and the
    feeling the appraisal formed of it, already bent by the temperament."""

    def __init__(self, person, event, retold, feeling, conclusion, valence, intensity, at):
        self.person = person
        self.event = event
        self.retold = retold
        self.feeling = feeling
        self.conclusion = conclusion
        self.valence = valence
        self.intensity = intensity
        self.at = at
