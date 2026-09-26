class Affect:
    """The feeling of one moment as the appraisal formed it: the words for it, the conclusion,
    valence and intensity. This, not the mood-coloured feeling of the reply call, is what is kept."""

    def __init__(self, feeling, conclusion, valence, intensity):
        self.feeling = feeling
        self.conclusion = conclusion
        self.valence = valence
        self.intensity = intensity
