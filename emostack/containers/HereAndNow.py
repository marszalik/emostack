class HereAndNow:
    """The situation as the senses deliver it in one call: when it is, who the being is talking
    with, who else is present, and the senses. Values of the moment, no records."""

    def __init__(self, now, beingName, person, otherSessions, senses):
        self.now = now
        self.beingName = beingName
        self.person = person
        self.otherSessions = list(otherSessions or [])
        self.senses = senses
