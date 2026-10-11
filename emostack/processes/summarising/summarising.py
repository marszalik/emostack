from emostack.core.ProcessorError import ProcessorError
from emostack.episode.Rendering import Rendering
from emostack.processes.summarising.SummarisingContext import SummarisingContext


class summarising:
    """Folds what leaves the focus into its summary: the events only, what happened, what was said and
    what the being recalled, in its own voice, without the feelings, which the state carries, and
    without the conclusions."""

    temperature = 0.4

    def __init__(self, processor, threadCap=40):
        self.processor = processor
        self.threadCap = threadCap

    def fold(self, beingName, previous, entries, before):
        """Returns one part of the summary, what was brought in from before (`before`) or the
        conversation itself, with `entries` folded in; None when the call failed and the entries
        should stay in view."""
        context = SummarisingContext(beingName, previous, self._events(entries)[-self.threadCap:], before)
        if not context.events:
            return previous
        try:
            answer = self.processor.chat(context.system(), context.user(), self.temperature,
                                         purpose="summarising")
        except ProcessorError:
            return None
        return (answer or "").strip() or None

    @staticmethod
    def _events(entries):
        events = []
        for entry in entries:
            rendering = Rendering.RETOLD if entry.isFromBefore() else Rendering.AS_IT_HAPPENED
            episodes = sorted(entry.record.episodes or [], key=lambda episode: episode.happenedAt)
            text = " / ".join(t for t in (episode.text(rendering) for episode in episodes) if t)
            if text:
                events.append((entry, text))
        return events
