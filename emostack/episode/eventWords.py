from emostack.core.promptTemplate import promptTemplate


class eventWords:
    """An event as it happened, in the words it is kept in."""

    def __init__(self):
        self._words = promptTemplate.beside(__file__, "event.prompt")

    def said(self, person, words):
        return self._words.fill("said", PERSON=person, WORDS=words.strip())

    def replied(self, event, beingName, words):
        return self._words.fill("replied", EVENT=event, BEING=beingName, WORDS=words.strip())

    def entered(self, person):
        return self._words.fill("entered", PERSON=person)

    def left(self, person):
        return self._words.fill("left", PERSON=person)

    def isSaid(self, text):
        """Does this event carry words someone said?"""
        marker = self._words.text("said").split("«PERSON»", 1)[1].split("«WORDS»", 1)[0]
        return marker in (text or "")
