from emostack.containers.FocusEntry import FocusEntry
from emostack.episode.Rendering import Rendering


class Focus:
    """Attention on this conversation: what was said, what the being said back, and what surfaced
    meanwhile, in order. Capped only to protect the context."""

    def __init__(self, cap=100):
        self.cap = cap
        self.entries = []

    def pushMoment(self, record):
        self._push(FocusEntry(record, FocusEntry.THIS_CONVERSATION))

    def pushEvoked(self, record):
        if record.id in self.ids():
            return
        self._push(FocusEntry(record, FocusEntry.EVOKED_FROM_BEFORE))

    def ids(self):
        return {entry.record.id for entry in self.entries}

    def eventsAsItHappened(self):
        return {episode.text(Rendering.AS_IT_HAPPENED)
                for entry in self.entries for episode in (entry.record.episodes or [])}

    def moments(self, person=None):
        return [entry for entry in self.entries if not entry.isEvoked()
                and (person is None or entry.record.author.isPerson(person))]

    def _push(self, entry):
        self.entries.append(entry)
        if len(self.entries) > self.cap:
            self.entries = self.entries[-self.cap:]
