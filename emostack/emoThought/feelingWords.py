from emostack.core.promptTemplate import promptTemplate


class feelingWords:
    """A feeling in words instead of numbers: its quality from the valence, its strength from the
    felt intensity. The LLM model reads words, not 'intensity 0.73'."""

    def __init__(self):
        self._words = promptTemplate.beside(__file__, "affect.prompt")

    def describe(self, valence, felt):
        return self._words.fill("description", QUALITY=self._words.text(self._quality(valence)),
                                STRENGTH=self._words.text(self._strength(felt)))

    @staticmethod
    def _strength(felt):
        if felt >= 0.85:
            return "strengthOverwhelming"
        if felt >= 0.6:
            return "strengthStrong"
        if felt >= 0.4:
            return "strengthNoticeable"
        if felt >= 0.2:
            return "strengthQuiet"
        return "strengthTrace"

    @staticmethod
    def _quality(valence):
        if valence <= -0.6:
            return "qualityVeryPainful"
        if valence < -0.05:
            return "qualityUnpleasant"
        if valence <= 0.05:
            return "qualityIndifferent"
        if valence < 0.6:
            return "qualityPleasant"
        return "qualityVeryPleasant"
