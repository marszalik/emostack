from emostack.core.ProcessorError import ProcessorError
from emostack.episode.Rendering import Rendering
from emostack.processes.lastDays.LastDaysContext import LastDaysContext


class lastDays:
    """Keeps the last days of one being. At the end of every conversation, today is rewritten whole
    with the events of that conversation added, in the being's own voice, events only. At the night,
    yesterday is folded into the days before, today becomes yesterday and a new today begins empty.
    Switched off (an ablation), it keeps nothing and shows nothing. When a call fails, the account
    stands as it was."""

    temperature = 0.4

    def __init__(self, processor, repository, being, enabled=True):
        self.processor = processor
        self.repository = repository
        self.being = being
        self.enabled = bool(enabled)
        self.context = LastDaysContext(being.name)
        self._current = None

    def current(self):
        """The last days as they stand, read from store once per assembly; None when switched off."""
        if not self.enabled:
            return None
        if self._current is None:
            self._current = self.repository.get(self.being.id)
        return self._current

    def conversationEnded(self, focus):
        """Folds the conversation that just ended into today: every moment of it, as retold."""
        if not self.enabled:
            return
        events = []
        for entry in focus.moments():
            episodes = sorted(entry.record.episodes or [], key=lambda episode: episode.happenedAt)
            events.extend(text for text in (episode.text(Rendering.RETOLD) for episode in episodes) if text)
        if not events:
            return
        days = self.current()
        text = self._chat(self.context.systemToday(), self.context.userToday(days.today, events))
        if text:
            days.today = text
            self.repository.save(self.being.id, days)

    def night(self):
        """The night turns the days: yesterday is folded into the days before, today becomes yesterday."""
        if not self.enabled:
            return
        days = self.current()
        if days.isEmpty():
            return
        before = days.before
        if days.yesterday:
            folded = self._chat(self.context.systemBefore(), self.context.userBefore(days.before, days.yesterday))
            before = folded or "\n".join(part for part in (days.before, days.yesterday) if part)
        days.turn(before)
        self.repository.save(self.being.id, days)

    def _chat(self, system, user):
        try:
            answer = self.processor.chat(system, user, self.temperature, purpose="lastDays")
        except ProcessorError:
            return ""
        return (answer or "").strip()
