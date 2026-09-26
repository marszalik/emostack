from emostack.core.promptTemplate import promptTemplate
from emostack.episode.Rendering import Rendering


class AssociationFilterContext:
    """What the association filter sees: the trigger and the recall candidates, each by the event
    that surfaced it. Nothing else."""

    def __init__(self, words, candidates, keepAtMost, feelingWords):
        self.words = words
        self.candidates = list(candidates)
        self.keepAtMost = keepAtMost
        self.feelingWords = feelingWords
        self.template = promptTemplate.beside(__file__, "associationFilter.prompt")

    def system(self):
        return self.template.text("system")

    def user(self):
        listing = "\n".join(
            self.template.fill("candidate", INDEX=index,
                               FEELING=self.feelingWords.describe(record.valence, record.intensity),
                               EVENT=self._event(record), CONCLUSION=record.conclusion)
            for index, record in enumerate(self.candidates))
        return self.template.fill("user", INPUT=self.words, CANDIDATES=listing, MAXKEEP=self.keepAtMost)

    def responseFormat(self):
        return self.template.json("responseFormat")

    @staticmethod
    def _event(record):
        if record.isConstruct():
            return record.statement()
        if record.hitEpisode is not None:
            return record.hitEpisode.text(Rendering.RETOLD)
        episodes = sorted(record.episodes or [], key=lambda episode: episode.happenedAt)
        return " / ".join(text for text in (episode.text(Rendering.RETOLD) for episode in episodes) if text)
