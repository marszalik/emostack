from emostack.core.promptTemplate import promptTemplate


class SummarisingContext:
    """What summarising sees: the summary so far and the events leaving the focus, each marked as
    lived in this conversation, recalled, or brought in from before; nothing of the feelings or the
    conclusions."""

    def __init__(self, beingName, previous, events):
        """events: (focus entry, its events as text), oldest first."""
        self.beingName = beingName
        self.previous = (previous or "").strip()
        self.events = list(events)
        self.template = promptTemplate.beside(__file__, "summarising.prompt")

    def system(self):
        return self.template.fill("system", BEING=self.beingName)

    def user(self):
        previous = self.previous or self.template.text("nothingYet")
        return self.template.fill("user", PREVIOUS=previous, BODY="\n".join(self._line(entry, text)
                                                                          for entry, text in self.events),
                                  BEING=self.beingName)

    def _line(self, entry, text):
        if entry.isEvoked():
            return self.template.fill("recalled", EVENT=text)
        if entry.isCarried():
            return self.template.fill("broughtIn", EVENT=text)
        return self.template.fill("happened", EVENT=text)
