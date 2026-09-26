from emostack.core.promptTemplate import promptTemplate
from emostack.episode.Rendering import Rendering


class ReplyContext:
    """What the reply call sees, in the order the LLM model reads it: here and now with the senses;
    the state, each feeling with its words, strength and conclusion; the accessibility slot; the
    conversation summary; the applicable dispositions; the focus, opened by the retold episodes the
    feelings of the state rest on, then this conversation as it happened, each moment under its
    feeling, and evoked memories retold; and what is heard. Nothing is withheld."""

    WORDS = "words"
    ARRIVAL = "arrival"
    DEPARTURE = "departure"

    def __init__(self, kind, hereAndNow, state, focusEntries, clock, feelingWords, fading, rumination,
                 words="", held=None, summary="", dispositions=None):
        self.kind = kind
        self.hereAndNow = hereAndNow
        self.state = state
        self.focusEntries = list(focusEntries)
        self.clock = clock
        self.feelingWords = feelingWords
        self.fading = fading
        self.rumination = rumination
        self.words = words
        self.held = list(held or [])
        self.summary = summary
        self.dispositions = list(dispositions or [])
        self.stateIndex = []
        self.parts = promptTemplate.beside(__file__, "reply.prompt")
        self.template = self._ownTemplate()

    def _ownTemplate(self):
        return promptTemplate.beside(__file__, "reply.prompt")

    # ---- the call ----

    def system(self):
        return self.template.text("system")

    def user(self):
        if self.kind == self.ARRIVAL:
            schema = self.template.text("schemaArrival")
            layout = "userArrival"
        else:
            schema = self.template.fill("schemaWords", INTERLOCUTOR=self.hereAndNow.person)
            layout = "userWords"
        return self.template.fill(layout, CONTEXT=self.render(), INTERLOCUTOR=self.hereAndNow.person,
                                  INPUT=self.words, SCHEMA=schema)

    def responseFormat(self):
        return self.template.json("responseFormatArrival" if self.kind == self.ARRIVAL
                                  else "responseFormatWords")

    # ---- the context ----

    def render(self):
        self.stateIndex = []
        moved = []
        lines = [self.parts.fill("header", BEING=self.hereAndNow.beingName, PERSON=self.hereAndNow.person)]
        lines.append("\n" + self.hereAndNow.senses.render())
        lines.extend(self._presence())
        self._renderState(lines, moved)
        self._renderSlot(lines)
        if (self.summary or "").strip():
            lines.append(self.parts.fill("summary", TEXT=self.summary.strip().replace("\n", "\n  ")))
        self._renderDispositions(lines)
        self._renderFocus(lines, moved)
        return "\n".join(lines)

    def _presence(self):
        now = self.hereAndNow.now
        lines = [self.parts.fill("stateHead", NOW=self.clock.formatAbsolute(now), UNIX=f"{now:.0f}")]
        others = self.hereAndNow.otherSessions
        if not others:
            lines.append(self.parts.text("noOthers"))
            return lines
        lines.append(self.parts.text("othersHead"))
        for session in others:
            last = (self.clock.formatAgo(session.lastTurnAt, now) if session.lastTurnAt
                    else self.parts.text("otherNoTurn"))
            lines.append(self.parts.fill("other", PERSON=session.person,
                                         DURATION=self.clock.formatDuration(now - session.startedAt),
                                         LAST=last, TURNS=session.turnCount))
        return lines

    def _renderState(self, lines, moved):
        entries = list(self.state or [])
        if not entries:
            lines.append(self.parts.text("noFeelings"))
            return
        now = self.hereAndNow.now
        inConversation = self._conversationEvents()
        lines.append(self.parts.text("feelingsHead"))
        clusters = sorted(self.rumination.cluster(entries),
                          key=lambda cluster: -cluster.representative.feltAt(now, self.fading))
        for cluster in clusters:
            record = cluster.representative
            index = ""
            if not record.isConstruct():
                index = self.parts.fill("index", NUMBER=len(self.stateIndex))
                self.stateIndex.append(record.id)
            lines.append(self.parts.fill(
                "feeling", INDEX=index, AGO=self.clock.formatAgo(record.happenedAt, now),
                TAG=self._tag(record), WORDS=self._words(record), FEELING=record.feeling,
                RECUR=self.parts.fill("recur", COUNT=cluster.count) if cluster.count > 1 else "",
                CONCLUSION=self.parts.fill("conclusion", TEXT=record.conclusion) if record.conclusion else ""))
            for episode in record.episodes or []:
                if episode.text(Rendering.AS_IT_HAPPENED) in inConversation:
                    continue
                moved.append(self.parts.fill("beforeEvent", AGO=self.clock.formatAgo(episode.happenedAt, now),
                                             EVENT=episode.text(Rendering.RETOLD)))

    def _renderSlot(self, lines):
        if not self.held:
            return
        now = self.hereAndNow.now
        lines.append(self.parts.text("slotHead"))
        for construct in self.held:
            lines.append(self.parts.fill("slotEntry", AGO=self.clock.formatAgo(construct.happenedAt, now),
                                         STATEMENT=construct.statement()))

    def _renderDispositions(self, lines):
        if not self.dispositions:
            return
        lines.append(self.parts.text("dispositionsHead"))
        lines.extend(self.parts.fill("disposition", RULE=rule) for rule in self.dispositions)

    def _renderFocus(self, lines, moved):
        stateIds = {record.id for record in (self.state or [])}
        entries = [entry for entry in self.focusEntries
                   if not (entry.isEvoked() and entry.record.id in stateIds)]
        if not entries and not moved:
            return
        lines.append(self.parts.text("focusHead"))
        if moved:
            lines.append(self.parts.text("beforeHead"))
            lines.extend(moved)
            lines.append(self.parts.text("beforeEnd"))
        lines.append(self.parts.text("conversationHead"))
        for entry in entries:
            lines.extend(self._entry(entry))

    def _entry(self, entry):
        now = self.hereAndNow.now
        record = entry.record
        rendering = Rendering.RETOLD if entry.isEvoked() else Rendering.AS_IT_HAPPENED
        episodes = sorted(record.episodes or [], key=lambda episode: episode.happenedAt)
        texts = [episode.text(rendering) for episode in episodes if episode.text(rendering)]
        head = texts[0] if len(texts) == 1 else ""
        line = self.parts.fill("entry", AGO=self.clock.formatAgo(record.happenedAt, now), TAG=self._tag(record),
                               WORDS=self._words(record), FEELING=record.feeling,
                               EVENT=self.parts.fill("entryEvent", EVENT=head) if head else "")
        subs = []
        if len(texts) > 1:
            subs = [self.parts.fill("subEvent", AGO=self.clock.formatAgo(episode.happenedAt, now),
                                    EVENT=episode.text(rendering)) for episode in episodes]
        return [line] + subs

    # ---- helpers ----

    def _words(self, record):
        return self.feelingWords.describe(record.valence, record.feltAt(self.hereAndNow.now, self.fading))

    def _conversationEvents(self):
        return {episode.text(Rendering.AS_IT_HAPPENED)
                for entry in self.focusEntries if not entry.isEvoked()
                for episode in (entry.record.episodes or [])}

    def _tag(self, record):
        person = self.hereAndNow.person
        if record.isGiven():
            return self.parts.text("tagGiven")
        events = " / ".join(episode.text(Rendering.AS_IT_HAPPENED) for episode in (record.episodes or []))
        mentions = f"{events} {record.conclusion}".lower()
        author = record.author.name
        if person and person.lower() in mentions:
            if record.author.isPerson(person):
                return self.parts.fill("tagAbout", PERSON=person)
            return self.parts.fill("tagAboutToldBy", PERSON=person, TELLER=author)
        if record.author.isPerson(person):
            return self.parts.text("tagSamePerson")
        return self.parts.fill("tagWith", PERSON=author)
