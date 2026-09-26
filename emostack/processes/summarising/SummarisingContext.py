from emostack.core.promptTemplate import promptTemplate


class SummarisingContext:
    """What summarising sees: the events of the focus with this person, and nothing of the
    feelings."""

    def __init__(self, beingName, events):
        self.beingName = beingName
        self.events = list(events)
        self.template = promptTemplate.beside(__file__, "summarising.prompt")

    def system(self):
        return self.template.fill("system", BEING=self.beingName)

    def user(self):
        return self.template.fill("user", BODY="\n".join(self.events), BEING=self.beingName)
