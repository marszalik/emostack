from emostack.core.ProcessorError import ProcessorError
from emostack.episode.Rendering import Rendering
from emostack.processes.summarising.SummarisingContext import SummarisingContext


class summarising:
    """Folds the conversation into its gist: what happened and what was said, in the being's own
    voice, without the emotions, which the state carries."""

    temperature = 0.4
    minimumEvents = 3

    def __init__(self, processor, threadCap=40):
        self.processor = processor
        self.threadCap = threadCap

    def refresh(self, beingName, person, focus, previous):
        events = []
        for entry in focus.entries:
            if not entry.record.author.isPerson(person):
                continue
            rendering = Rendering.RETOLD if entry.isEvoked() else Rendering.AS_IT_HAPPENED
            episodes = sorted(entry.record.episodes or [], key=lambda episode: episode.happenedAt)
            text = " / ".join(t for t in (episode.text(rendering) for episode in episodes) if t)
            if text:
                events.append(text)
        if len(events) < self.minimumEvents:
            return previous
        context = SummarisingContext(beingName, events[-self.threadCap:])
        try:
            answer = self.processor.chat(context.system(), context.user(), self.temperature,
                                         purpose="summarising")
        except ProcessorError:
            return previous
        return (answer or "").strip() or previous
