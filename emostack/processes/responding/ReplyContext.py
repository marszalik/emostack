from emostack.core.promptTemplate import promptTemplate
from emostack.episode.Rendering import Rendering


class ReplyContext:
    """What the reply call sees, in the order the LLM model reads it: here and now with the senses;
    the state, each feeling with its words, strength and conclusion; the accessibility slot, when its
    thoughts are not placed in the line; the applicable dispositions; the focus: the summary of what
    has left view, then the line in the order things came into view, the feelings brought in from
    before and evoked memories retold, the moments as they happened, each under its feeling unless
    the feeling is already in the state; and what is heard. Nothing is withheld."""

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
        self.parts = promptTemplate.beside(__file__, "reply.prompt")
        self.template = self._ownTemplate()

    def _ownTemplate(self):
        return promptTemplate.beside(__file__, "reply.prompt")

    # ---- the call ----

    def system(self):
        return self.template.text("system")

    def user(self, forModel=""):
        """The call as the model `forModel` reads it: a block worded for that model replaces the common one."""
        if self.kind == self.ARRIVAL:
            schema = self.template.text("schemaArrival")
            layout = "userArrival"
        else:
            schema = self.template.fill("schemaWords", INTERLOCUTOR=self.hereAndNow.person)
            layout = "userWords"
        return self.template.fill(layout, forModel, CONTEXT=self.render(), INTERLOCUTOR=self.hereAndNow.person,
                                  INPUT=self.words, SCHEMA=schema)

    def responseFormat(self):
        return self.template.json("responseFormatArrival" if self.kind == self.ARRIVAL
                                  else "responseFormatWords")

    # ---- the context ----

    def render(self):
        lines = [self.parts.fill("header", BEING=self.hereAndNow.beingName, PERSON=self.hereAndNow.person)]
        lines.append("\n" + self.hereAndNow.senses.render())
        lines.extend(self._presence())
        self._renderState(lines)
        self._renderSlot(lines)
        self._renderDispositions(lines)
        self._renderFocus(lines)
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

    def _renderState(self, lines):
        entries = list(self.state or [])
        if not entries:
            lines.append(self.parts.text("noFeelings"))
            return
        now = self.hereAndNow.now
        lines.append(self.parts.text("feelingsHead"))
        clusters = sorted(self.rumination.cluster(entries),
                          key=lambda cluster: -cluster.representative.feltAt(now, self.fading))
        for cluster in clusters:
            record = cluster.representative
            lines.append(self.parts.fill(
                "feeling", AGO=self.clock.formatAgo(record.happenedAt, now),
                TAG=self._tag(record), WORDS=self._words(record), FEELING=record.feeling,
                RECUR=self.parts.fill("recur", COUNT=cluster.count) if cluster.count > 1 else "",
                CONCLUSION=self.parts.fill("conclusion", TEXT=record.conclusion) if record.conclusion else ""))

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

    def _renderFocus(self, lines):
        if (self.summary or "").strip():
            lines.append(self.parts.fill("summary", TEXT=self.summary.strip().replace("\n", "\n  ")))
        if not self.focusEntries:
            return
        lines.append(self.parts.text("focusHead"))
        lines.append(self.parts.text("conversationHead"))
        for entry in self.focusEntries:
            lines.extend(self._entry(entry))

    def _entry(self, entry):
        """A held thought is its own statement. An entry whose feeling is in the state shows only its
        event: the feeling is not repeated."""
        now = self.hereAndNow.now
        record = entry.record
        if entry.isHeldThought():
            return [self.parts.fill("entryThought", AGO=self.clock.formatAgo(record.happenedAt, now),
                                    STATEMENT=record.statement())]
        rendering = Rendering.RETOLD if entry.isFromBefore() else Rendering.AS_IT_HAPPENED
        episodes = sorted(record.episodes or [], key=lambda episode: episode.happenedAt)
        texts = [episode.text(rendering) for episode in episodes if episode.text(rendering)]
        head = texts[0] if len(texts) == 1 else ""
        if self._isFelt(record):
            line = self.parts.fill("entryEventsOnly", AGO=self.clock.formatAgo(record.happenedAt, now),
                                   TAG=self._tag(record), EVENT=head)
        else:
            line = self.parts.fill("entry", AGO=self.clock.formatAgo(record.happenedAt, now),
                                   TAG=self._tag(record), WORDS=self._words(record), FEELING=record.feeling,
                                   EVENT=self.parts.fill("entryEvent", EVENT=head) if head else "")
        subs = []
        if len(texts) > 1:
            subs = [self.parts.fill("subEvent", AGO=self.clock.formatAgo(episode.happenedAt, now),
                                    EVENT=episode.text(rendering)) for episode in episodes]
        return [line] + subs

    # ---- helpers ----

    def _words(self, record):
        return self.feelingWords.describe(record.valence, record.feltAt(self.hereAndNow.now, self.fading))

    def _isFelt(self, record):
        return any(felt.id == record.id for felt in (self.state or []))

    def _lineEvents(self):
        return {episode.text(Rendering.AS_IT_HAPPENED)
                for entry in self.focusEntries if not entry.isHeldThought()
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
