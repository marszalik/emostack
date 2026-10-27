class LastDays:
    """What the being carries of its last days without attending to it: three accounts in its own
    voice, events only, without the feelings, which the state carries, and without the conclusions.
    Today so far, rewritten at the end of every conversation of the day; yesterday; and the days
    before, folded. It stands beside the focus, not in it: attention is the focus alone, this is the
    background every reply is written against. Kept in store between conversations; it turns at the
    night, when today becomes yesterday and yesterday is folded into the days before."""

    def __init__(self, today="", yesterday="", before=""):
        self.today = (today or "").strip()
        self.yesterday = (yesterday or "").strip()
        self.before = (before or "").strip()

    def isEmpty(self):
        return not (self.today or self.yesterday or self.before)

    def turn(self, before):
        """The night: today becomes yesterday, the days before take the folded text `before`, and
        today starts empty."""
        self.before = (before or "").strip()
        self.yesterday, self.today = self.today, ""
