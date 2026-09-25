from emostack.core.ProcessorError import ProcessorError
from emostack.processes.sleep.ConsolidationPlanContext import ConsolidationPlanContext


class sleep:
    """Sleep folds the day and forgets what is weak for its age.

    Consolidation: the LLM model proposes groups; the code decides what may serve as an anchor (a
    lived feeling, strong enough, not weaker than what it absorbs) and what may never be absorbed
    (constructs and given records). The absorbed records' episodes move under the anchor, so nothing
    that happened is summarised away, and the anchor keeps their accumulated strength.

    Forgetting: a record weaker than the threshold for its age is removed with its episodes.
    Constructs and given records are never forgotten."""

    temperature = 0.3

    def __init__(self, processor, hippocampus, clock, feelingWords, threshold, anchorMinimum=0.4,
                 episodesPerRecord=6):
        self.processor = processor
        self.hippocampus = hippocampus
        self.clock = clock
        self.feelingWords = feelingWords
        self.threshold = threshold
        self.anchorMinimum = anchorMinimum
        self.episodesPerRecord = episodesPerRecord

    def consolidate(self, being, since):
        """Folds the records that happened since `since`. Returns the number of records absorbed."""
        records = [record for record in self.hippocampus.all() if record.happenedAt >= since]
        if len(records) < 2:
            return 0
        self.hippocampus.withEpisodes(records, self.episodesPerRecord)
        context = ConsolidationPlanContext(being.name, records, self.clock, self.feelingWords)
        try:
            answer = self.processor.chatJson(context.system(), context.user(), self.temperature,
                                             context.responseFormat(), purpose="consolidation")
        except ProcessorError:
            return 0
        byId = {record.id: record for record in records}
        absorbed = 0
        for group in answer.get("groups", []):
            anchor = byId.get(str(group.get("anchor_id", "")))
            if anchor is None or anchor.isConstruct() or anchor.intensity < self.anchorMinimum:
                continue
            members = [byId[recordId] for recordId in (group.get("absorbs") or [])
                       if recordId in byId and recordId != anchor.id
                       and not ConsolidationPlanContext.isProtected(byId[recordId])
                       and byId[recordId].intensity <= anchor.intensity]
            if not members:
                continue
            keep = 1.0 - max(0.0, min(1.0, anchor.intensity))
            for member in members:
                keep *= 1.0 - max(0.0, min(1.0, member.intensity))
            self.hippocampus.setIntensity(anchor, 1.0 - keep)
            for member in members:
                self.hippocampus.moveEpisodes(member, anchor)
                self.hippocampus.forget(member)
                del byId[member.id]
                absorbed += 1
        return absorbed

    def forget(self):
        """Removes what is too weak for its age. Returns the removed records."""
        now = self.clock.now()
        removed = []
        for record in self.hippocampus.all():
            if ConsolidationPlanContext.isProtected(record):
                continue
            if self.threshold.isTooWeak(record.intensity, (now - record.lastFelt) / 86400.0):
                self.hippocampus.forget(record)
                removed.append(record)
        return removed
