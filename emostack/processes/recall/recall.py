import math
import re

from emostack.episode.Rendering import Rendering
from emostack.processes.recall.Candidate import Candidate
from emostack.processes.recall.RecallResult import RecallResult

try:
    import numpy
except ImportError:
    numpy = None


class recall:
    """What comes to mind. A record's score is its similarity to the words multiplied by its
    present felt strength, plus a bonus when it mentions the interlocutor or a name in the words.
    Search runs over episodes too: an event can lift its feeling into the candidates. The best
    candidates are collapsed when they are one recurring thought, anything still felt at the floor
    passes, and the association filter chooses among the rest. Records of this conversation are
    not a memory: they are already in view as the conversation."""

    namePattern = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-ZŁŚŻŹĆŃÓĘĄ][a-ząćęłńóśźż]{2,})\b")

    def __init__(self, hippocampus, embedder, filter, rumination, fading, clock, candidates=10,
                 nameBonus=0.5, strengthPasses=0.5, episodesPerCandidate=3):
        self.hippocampus = hippocampus
        self.embedder = embedder
        self.filter = filter
        self.rumination = rumination
        self.fading = fading
        self.clock = clock
        self.candidates = candidates
        self.nameBonus = nameBonus
        self.strengthPasses = strengthPasses
        self.episodesPerCandidate = episodesPerCandidate

    # ---- the involuntary path: what the words bring to mind ----

    def involuntary(self, words, person, conversationIds):
        candidates = self._collapsed(self.search(words, person))
        now = self.clock.now()
        passed = [c for c in candidates if c.record.feltAt(now, self.fading) >= self.strengthPasses]
        rest = [c for c in candidates if c.record.feltAt(now, self.fading) < self.strengthPasses]
        # the filter always has a say on the rest, even when the strong ones fill the room: it also
        # reads whether the words ask the being to recall a moment of its own
        room = max(1, self.filter.keepAtMost - len(passed))
        verdict = self.filter.choose(words, [c.record for c in rest], room)
        records = [c.record for c in passed] + verdict.kept
        records = [record for record in records if record.id not in conversationIds]
        return RecallResult(records, verdict.asksForMemory, verdict.asksForOwn)

    # ---- deliberate paths: what the being searches for ----

    def deliberate(self, query, person, conversationIds):
        """A search the being makes goes through the same filter, so that 'found' means genuinely
        associated. A query that names a person is answered only by records of that person."""
        candidates = [c for c in self._collapsed(self.search(query, person))
                      if c.record.id not in conversationIds]
        names = [match.group(1) for match in self.namePattern.finditer(query)]
        if person and person.lower() in query.lower():
            names.append(person)
        if names:
            mentioning = self.hippocampus.mentioning(list(set(names)))
            candidates = [c for c in candidates
                          if (c.record.author.name in names) or c.record.id in mentioning]
            if not candidates:
                return []
        return self.filter.choose(query, [c.record for c in candidates]).kept

    def plain(self, query, person=None):
        """The nearest records, unfiltered: what a reflection's own search or an arrival's search
        brings up."""
        return [candidate.record for candidate in self.search(query, person)]

    def ownOfKind(self, kind, limit=3):
        return self.hippocampus.constructsOfKind(kind)[:limit]

    def aboutPerson(self, person, limit):
        """At an arrival: what the being has lived with this person or heard about them."""
        mentioning = self.hippocampus.mentioning([person])
        known = [record for record in self.hippocampus.all()
                 if record.author.isPerson(person) or record.id in mentioning]
        known.sort(key=lambda record: record.intensity, reverse=True)
        return known[:limit]

    def knowsPerson(self, person, conversationIds):
        mentioning = self.hippocampus.mentioning([person])
        return any(record.id not in conversationIds
                   and (record.author.isPerson(person) or record.id in mentioning)
                   for record in self.hippocampus.all())

    # ---- scoring ----

    def search(self, text, person=None):
        vector = self.embedder.embed(text)
        records = [record for record in self.hippocampus.all()
                   if record.vector and len(record.vector) == len(vector)]
        if not records:
            return []
        now = self.clock.now()
        names = self._names(text, person)
        scored = []
        for record, similarity in zip(records, self._similarities(vector, records)):
            score = similarity * record.feltAt(now, self.fading)
            if names and self._mentions(self._recordText(record), names):
                score += self.nameBonus
            scored.append(Candidate(score, similarity, record))
        position = {record.id: index for index, record in enumerate(records)}
        episodes = [episode for episode in self.hippocampus.searchableEpisodes()
                    if len(episode.vector) == len(vector) and episode.recordId in position]
        for episode, similarity in zip(episodes, self._similarities(vector, episodes)):
            index = position[episode.recordId]
            record = records[index]
            score = float(similarity) * record.feltAt(now, self.fading)
            if names and self._mentions(episode.asItHappened, names):
                score += self.nameBonus
            if score > scored[index].score:
                scored[index] = Candidate(score, float(similarity), record)
                record.hitEpisode = episode
        scored.sort(key=lambda candidate: candidate.score, reverse=True)
        top = scored[:self.candidates]
        self.hippocampus.withEpisodes([candidate.record for candidate in top], self.episodesPerCandidate)
        return top

    def _collapsed(self, candidates):
        if len(candidates) <= 1:
            return candidates
        clusters = self.rumination.cluster([candidate.record for candidate in candidates])
        if len(clusters) == len(candidates):
            return candidates
        byId = {candidate.record.id: candidate for candidate in candidates}
        kept = [max((byId[member.id] for member in cluster.members), key=lambda c: c.score)
                for cluster in clusters]
        kept.sort(key=lambda candidate: candidate.score, reverse=True)
        return kept

    def _names(self, text, person):
        names = {person.lower()} if person else set()
        names.update(match.group(1).lower() for match in self.namePattern.finditer(text or ""))
        return names

    @staticmethod
    def _recordText(record):
        if record.isConstruct():
            return f"{record.statement()} {record.conclusion}"
        return record.conclusion or ""

    @staticmethod
    def _mentions(text, names):
        lowered = (text or "").lower()
        return any(re.search(rf"\b{re.escape(name)}\b", lowered) for name in names)

    @staticmethod
    def _similarities(vector, items):
        if not items:
            return []
        if numpy is not None:
            matrix = numpy.array([item.vector for item in items], dtype=float)
            query = numpy.array(vector, dtype=float)
            query = query / (numpy.linalg.norm(query) or 1.0)
            norms = numpy.linalg.norm(matrix, axis=1)
            norms[norms == 0] = 1.0
            return list((matrix @ query) / norms)
        results = []
        normQuery = math.sqrt(sum(x * x for x in vector))
        for item in items:
            normItem = math.sqrt(sum(x * x for x in item.vector))
            dot = sum(x * y for x, y in zip(vector, item.vector))
            results.append(dot / (normQuery * normItem) if normQuery and normItem else 0.0)
        return results
