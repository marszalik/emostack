from emostack.core.promptTemplate import promptTemplate
from emostack.episode.Rendering import Rendering


class IntrospectionContext:
    """What introspection sees: here and now; the accessibility slot first, then the last records
    from the focus and the hippocampus with their episodes, without fading; what its own search
    brought; mid-turn, the moment the being stopped at; in a chain, the previous thought. The applicable
    dispositions, the conversation summary and the felt strength are withheld."""

    gapSeconds = 6 * 3600

    def __init__(self, beingName, now, entries, clock, feelingWords, person=None, previous=None, direction="",
                 recalled=None):
        """previous: (text, conclusion) of the thought or the moment the chain continues from."""
        self.beingName = beingName
        self.now = now
        self.entries = list(entries)
        self.clock = clock
        self.feelingWords = feelingWords
        self.person = person
        self.previous = previous
        self.direction = direction
        self.recalled = list(recalled or [])
        self.template = promptTemplate.beside(__file__, "introspection.prompt")

    def system(self):
        return self.template.text("system")

    def user(self):
        return self.template.fill("user", CONTEXT=self.render(), REFLECT_HEAD=self._head(),
                                  SCHEMA=self.template.text("schema"))

    def responseFormat(self):
        return self.template.json("responseFormat")

    def render(self):
        words = self.template
        lines = [words.fill("headConversation", BEING=self.beingName, PERSON=self.person) if self.person
                 else words.fill("headAlone", BEING=self.beingName),
                 words.fill("now", NOW=self.clock.formatAbsolute(self.now))]
        if not self.entries:
            lines.append(words.text("empty"))
            lines.extend(self._recalled())
            return "\n".join(lines)
        lines.append(words.text("stateHead"))
        since = self.now - self.entries[0].lastFelt
        if since > self.gapSeconds:
            lines.append(words.fill("gap", DURATION=self.clock.formatDuration(since)))
        lines.append(words.text("indexNote"))
        for index, record in enumerate(self.entries):
            events = self._events(record)
            lines.append(words.fill(
                "entry", INDEX=index, AGO=self.clock.formatAgo(record.happenedAt, self.now), WHO=self._who(record),
                WORDS=self.feelingWords.describe(record.valence, record.intensity), FEELING=record.feeling,
                EVENT=words.fill("entryEvent", EVENT=events[0]) if len(events) == 1 else "",
                CONCLUSION=record.conclusion))
            if len(events) > 1:
                lines.extend(words.fill("subEvent", EVENT=event) for event in events)
        lines.extend(self._recalled())
        return "\n".join(lines)

    def _recalled(self):
        if not self.recalled:
            return []
        lines = [self.template.text("recalledHead")]
        for record in self.recalled:
            lines.append(self.template.fill(
                "recalled", AGO=self.clock.formatAgo(record.happenedAt, self.now), WHO=self._who(record),
                WORDS=self.feelingWords.describe(record.valence, record.intensity), FEELING=record.feeling,
                EVENTS=" / ".join(self._events(record))))
        return lines

    def _head(self):
        if self.previous is not None:
            text, conclusion = self.previous
            direction = (self.template.fill("direction", INTENT=self.direction) if self.direction
                         else self.template.text("noDirection"))
            return self.template.fill("continuation", THOUGHT=text[:300], CONCLUSION=(conclusion or "")[:300],
                                      DIRECTION=direction)
        return self.template.text("reflect")

    def _who(self, record):
        if record.isConstruct():
            return self.template.text("whoSelf")
        if record.isGiven():
            return self.template.text("whoGiven")
        return self.template.fill("whoPerson", PERSON=record.author.name)

    @staticmethod
    def _events(record):
        if record.isConstruct():
            return [record.statement()]
        episodes = sorted(record.episodes or [], key=lambda episode: episode.happenedAt)
        return [text for text in (episode.text(Rendering.RETOLD) for episode in episodes) if text]
