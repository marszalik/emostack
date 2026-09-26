from emostack.core.promptTemplate import promptTemplate
from emostack.episode.Rendering import Rendering


class ConsolidationPlanContext:
    """What consolidation sees: the records of the awake period with their episodes, in the order
    they happened. Constructs and given records are marked as candidates that may never be
    absorbed."""

    def __init__(self, beingName, records, clock, feelingWords):
        self.beingName = beingName
        self.records = sorted(records, key=lambda record: record.happenedAt)
        self.clock = clock
        self.feelingWords = feelingWords
        self.template = promptTemplate.beside(__file__, "consolidationPlan.prompt")

    @staticmethod
    def isProtected(record):
        return record.isConstruct() or record.isGiven()

    def system(self):
        return self.template.text("system")

    def user(self):
        listing = "\n".join(self._line(record) for record in self.records)
        return self.template.fill("user", BEING=self.beingName, COUNT=len(self.records), LISTING=listing)

    def responseFormat(self):
        return self.template.json("responseFormat")

    def _line(self, record):
        if record.isGiven():
            tag = self.template.text("tagGiven")
        elif record.isConstruct():
            tag = self.template.text("tagSelf")
        else:
            tag = record.author.name
        if record.isConstruct():
            events = record.statement()
        else:
            episodes = sorted(record.episodes or [], key=lambda episode: episode.happenedAt)
            events = " / ".join(t for t in (episode.text(Rendering.RETOLD) for episode in episodes) if t)
        return self.template.fill(
            "record", ID=record.id, WHEN=self.clock.formatShort(record.happenedAt), TAG=tag,
            WORDS=self.feelingWords.describe(record.valence, record.intensity),
            PROTECTED=self.template.text("protected") if self.isProtected(record) else "",
            EVENTS=events, CONCLUSION=record.conclusion)
