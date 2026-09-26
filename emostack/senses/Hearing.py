class Hearing:
    """What hearing carries now: a person's words, an arrival, a departure."""

    WORDS = "hearingWords"
    ARRIVAL = "hearingArrival"
    DEPARTURE = "hearingDeparture"

    def __init__(self, carries, person):
        self.carries = carries
        self.person = person
