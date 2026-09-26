from emostack.core.promptTemplate import promptTemplate
from emostack.episode.Rendering import Rendering
from emostack.processes.responding.ReplyContext import ReplyContext


class AppraisalContext(ReplyContext):
    """What the appraisal sees: the same here and now and trigger, what came to mind for this moment
    shown as memory, the conversation summary and the focus as events only. The state, the
    accessibility slot and the applicable dispositions are withheld, so that a bad mood colours the
    reply but not the memory."""

    def __init__(self, hereAndNow, remembered, focusEntries, clock, feelingWords, fading, rumination,
                 words, summary=""):
        super().__init__(ReplyContext.WORDS, hereAndNow, None, focusEntries, clock, feelingWords, fading,
                         rumination, words=words, summary=summary)
        self.remembered = list(remembered)

    def _ownTemplate(self):
        return promptTemplate.beside(__file__, "appraisal.prompt")

    def user(self):
        return self.template.fill("userWords", CONTEXT=self.render(), INTERLOCUTOR=self.hereAndNow.person,
                                  INPUT=self.words, SCHEMA=self.template.text("schemaWords"))

    def responseFormat(self):
        return self.template.json("responseFormatWords")

    def _renderState(self, lines, moved):
        lines.append(self.template.text("withheld"))
        if not self.remembered:
            return
        now = self.hereAndNow.now
        inConversation = self._conversationEvents()
        lines.append(self.template.text("rememberedHead"))
        for record in self.remembered:
            lines.append(self.template.fill("remembered", AGO=self.clock.formatAgo(record.happenedAt, now),
                                            TAG=self._tag(record),
                                            HEAD=(record.conclusion or record.feeling or "").strip()))
            for episode in record.episodes or []:
                if episode.text(Rendering.AS_IT_HAPPENED) in inConversation:
                    continue
                lines.append(self.template.fill("rememberedEvent",
                                                AGO=self.clock.formatAgo(episode.happenedAt, now),
                                                EVENT=episode.text(Rendering.RETOLD)))

    def _renderSlot(self, lines):
        return

    def _renderDispositions(self, lines):
        return

    def _entry(self, entry):
        now = self.hereAndNow.now
        record = entry.record
        rendering = Rendering.RETOLD if entry.isEvoked() else Rendering.AS_IT_HAPPENED
        episodes = sorted(record.episodes or [], key=lambda episode: episode.happenedAt)
        texts = [episode.text(rendering) for episode in episodes if episode.text(rendering)]
        head = texts[0] if len(texts) == 1 else ""
        line = self.parts.fill("entryEventsOnly", AGO=self.clock.formatAgo(record.happenedAt, now),
                               TAG=self._tag(record), EVENT=head)
        subs = []
        if len(texts) > 1:
            subs = [self.parts.fill("subEvent", AGO=self.clock.formatAgo(episode.happenedAt, now),
                                    EVENT=episode.text(rendering)) for episode in episodes]
        return [line] + subs
