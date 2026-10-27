from emostack.core.promptTemplate import promptTemplate


class LastDaysContext:
    """What the two calls that keep the last days see. At the end of a conversation: the account of
    today so far and the events of the conversation that just ended, oldest first. At the night: the
    account of the days before and the account of yesterday. Nothing of the feelings, the conclusions,
    the state or the held thoughts."""

    def __init__(self, beingName):
        self.beingName = beingName
        self.template = promptTemplate.beside(__file__, "lastDays.prompt")

    def systemToday(self):
        return self.template.fill("systemToday", BEING=self.beingName)

    def userToday(self, previous, events):
        return self.template.fill("userToday", PREVIOUS=self._previous(previous),
                                  BODY="\n".join(self.template.fill("event", EVENT=event) for event in events))

    def systemBefore(self):
        return self.template.fill("systemBefore", BEING=self.beingName)

    def userBefore(self, previous, yesterday):
        return self.template.fill("userBefore", PREVIOUS=self._previous(previous), YESTERDAY=yesterday.strip())

    def _previous(self, previous):
        return (previous or "").strip() or self.template.text("nothingYet")
