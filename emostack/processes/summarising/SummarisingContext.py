from emostack.core.promptTemplate import promptTemplate


class SummarisingContext:
    """What summarising sees: one part of the summary so far, and the events leaving the focus that
    belong to it, a memory marked as recalled; nothing of the feelings or the conclusions."""

    def __init__(self, beingName, previous, events, before):
        """events: (focus entry, its events as text), oldest first. before: the part of what the being
        brought in from before the conversation, else the part of the conversation itself."""
        self.beingName = beingName
        self.previous = (previous or "").strip()
        self.events = list(events)
        self.before = before
        self.template = promptTemplate.beside(__file__, "summarising.prompt")

    def system(self):
        return self.template.fill("systemBefore" if self.before else "systemDuring", BEING=self.beingName)

    def user(self):
        previous = self.previous or self.template.text("nothingYet")
        return self.template.fill("user", PREVIOUS=previous, BODY="\n".join(self._line(entry, text)
                                                                          for entry, text in self.events))

    def _line(self, entry, text):
        if entry.isEvoked():
            return self.template.fill("recalled", EVENT=text)
        return self.template.fill("happened", EVENT=text)
