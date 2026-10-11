from emostack.containers.ConversationSummary import ConversationSummary
from emostack.containers.FocusEntry import FocusEntry


class Focus:
    """Attention in Kahneman's sense, a limited resource: what the being is aware of in this
    conversation. One line in the order things came into view: the feelings brought in from before,
    the moments of the conversation, each memory after the moment that evoked it. Only the last `size`
    entries are in view; older ones are folded into the summary, their events without the feelings.
    Folded entries stay known to the conversation; `cap` only protects memory."""

    def __init__(self, size=8, cap=100):
        self.size = int(size)
        self.cap = cap
        self.entries = []
        self.summary = ConversationSummary()

    def pushCarried(self, record, at):
        """A feeling brought in enters the line once; once folded it does not come back with the
        state."""
        if record.id in {entry.record.id for entry in self.entries}:
            return
        self._push(FocusEntry(record, FocusEntry.CARRIED_FROM_BEFORE, at))

    def pushMoment(self, record, at):
        self._push(FocusEntry(record, FocusEntry.THIS_CONVERSATION, at))

    def pushEvoked(self, record, at):
        """A memory evoked again after it left view comes back into the line."""
        if record.id in self.ids():
            return
        self._push(FocusEntry(record, FocusEntry.EVOKED_FROM_BEFORE, at))

    def ids(self):
        """The records in view."""
        return {entry.record.id for entry in self.inView()}

    def inView(self):
        return [entry for entry in self.entries if not entry.folded]

    def overflow(self):
        """The oldest entries in view beyond the limit: what is leaving attention."""
        view = self.inView()
        return view[:max(0, len(view) - max(1, self.size))]

    def fold(self, entries, summaryText):
        for entry in entries:
            entry.folded = True
        self.summary.text = summaryText

    def line(self, current=(), held=()):
        """What is in view for this turn: the entries in view, then what came to mind in this turn and
        is not in the focus yet, with the held thoughts (construct, at) placed by the time they came to
        mind. Held thoughts do not count to the limit: the accessibility slot holds them."""
        known = self.ids()
        line = self.inView() + [entry for entry in current if entry.record.id not in known]
        thoughts = [FocusEntry(construct, FocusEntry.HELD_THOUGHT, at) for construct, at in held]
        return sorted(thoughts + line, key=lambda entry: entry.at)

    def moments(self, person=None):
        return [entry for entry in self.entries if entry.isMoment()
                and (person is None or entry.record.author.isPerson(person))]

    def lastMoment(self):
        moments = self.moments()
        return moments[-1].record if moments else None

    def _push(self, entry):
        self.entries.append(entry)
        if len(self.entries) > self.cap:
            self.entries = self.entries[-self.cap:]
