from emostack.action.ActionTarget import ActionTarget
from emostack.containers.Associations import Associations
from emostack.containers.FocusEntry import FocusEntry
from emostack.containers.HereAndNow import HereAndNow
from emostack.containers.State import State
from emostack.disposition.Situation import Situation
from emostack.emoThought.Author import Author
from emostack.emoThought.EmoThought import EmoThought
from emostack.emoThought.Strength import Strength
from emostack.episode.Episode import Episode
from emostack.episode.Rendering import Rendering
from emostack.processes.appraisal.AppraisalContext import AppraisalContext
from emostack.processes.appraisal.Affect import Affect
from emostack.processes.encoding.Moment import Moment
from emostack.processes.responding.ReplyContext import ReplyContext
from emostack.runtime.TurnOutcome import TurnOutcome
from emostack.senses.AttentionAndMemory import AttentionAndMemory
from emostack.senses.Hearing import Hearing
from emostack.senses.MemorySearch import MemorySearch
from emostack.senses.Senses import Senses


class turn:
    """The fast path: one trigger, in this order. The learned dispositions that fit are selected;
    recall brings up what the words bring to mind; the state is composed from the most recent
    records and the strongest associations; the focus line shows what is in view, with what came to
    mind placed after the moment that evoked it; reply generation produces the act. A search, or one of the engine's own searches when the person is unknown or asks about
    a moment or about the being's own dreams, beliefs, decisions or wants, adds to the associations
    and the reply is generated again; a pause to think runs reflection first. Appraisal forms the
    record to keep with the state withheld; the temperament bends it; encoding keeps it; what leaves
    the focus is folded into its summary. The last days stand beside the focus in every reply context;
    when the person leaves, the conversation is folded into today. Nothing on this path deliberates.

    One instance serves one trigger: the performer methods read the state of this trigger."""

    def __init__(self, conversation, hippocampus, slot, recall, responding, appraisal, encoding,
                 reconsolidation, summarising, selection, learning, reflection, presence, presenceKey,
                 carried, eventWords, probeWords, clock, feelingWords, fading, rumination, parameters,
                 lastDays=None):
        self.conversation = conversation
        self.being = conversation.being
        self.hippocampus = hippocampus
        self.slot = slot
        self.recall = recall
        self.responding = responding
        self.appraisal = appraisal
        self.encoding = encoding
        self.reconsolidation = reconsolidation
        self.summarising = summarising
        self.selection = selection
        self.learning = learning
        self.reflection = reflection
        self.presence = presence
        self.presenceKey = presenceKey
        self.carried = carried
        self.eventWords = eventWords
        self.probeWords = probeWords
        self.clock = clock
        self.feelingWords = feelingWords
        self.fading = fading
        self.rumination = rumination
        self.parameters = parameters
        self.lastDays = lastDays
        self.thoughts = []

    def take(self, trigger):
        return trigger.enter(self)

    # ---- an utterance ----

    def onUtterance(self, utterance):
        conversation = self.conversation
        person = utterance.person
        self.presence.heartbeat(conversation.sessionId)
        self.slot.load(self.clock.now())
        dispositions = self._applicable(person, utterance.words)
        conversation.lastDispositions = dispositions
        recalled = self.recall.involuntary(utterance.words, person, conversation.focus.ids())
        self.associations = Associations()
        self.associations.add(recalled.records)
        recent = self.hippocampus.mostRecentlyFelt(self.parameters["recentCount"], livedOnly=True)
        others = self.presence.others(self.presenceKey, conversation.sessionId)
        self.searches = []
        memorySize = self.hippocampus.size()
        hops = self.parameters["turnActionHops"]
        unknownProbe = kindProbe = momentProbe = False
        kept = None
        for self.hop in range(hops + 3):
            state, focusEntries = self._compose(recent)
            now = self.clock.now()
            senses = Senses(Hearing(Hearing.WORDS, person),
                            AttentionAndMemory(len(state), len(self.associations), memorySize, self.searches))
            hereAndNow = HereAndNow(now, self.being.name, person, others, senses)
            conversation.lastHereAndNow = hereAndNow
            context = ReplyContext(ReplyContext.WORDS, hereAndNow, state, focusEntries, self.clock,
                                   self.feelingWords, self.fading, self.rumination, words=utterance.words,
                                   held=self._slotBlock(), summary=conversation.focus.summary,
                                   dispositions=[disposition.rule for disposition in dispositions],
                                   lastDays=self._lastDays())
            reaction = self.responding.react(context)
            if reaction.failed:
                break
            kept = (reaction, state, focusEntries, hereAndNow)
            acts = reaction.action.target is not ActionTarget.WORLD
            searches = reaction.action.target is ActionTarget.MEMORY
            if not unknownProbe and not acts and not self.recall.knowsPerson(person, conversation.focus.ids()):
                unknownProbe = True
                query = self.probeWords.fill("probeUnknownPerson", PERSON=person)
                found = self.recall.deliberate(query, person, conversation.focus.ids())
                self.searches.append(MemorySearch(query, len(found)))
                self.associations.add(found)
                continue
            if recalled.asksForOwn and not kindProbe and not searches:
                kindProbe = True
                found = self.recall.ownOfKind(recalled.asksForOwn)
                self.searches.append(MemorySearch(self.probeWords.text(self._kindProbe(recalled.asksForOwn)),
                                                  len(found)))
                self.associations.add(found)
                continue
            if recalled.asksForMemory and not momentProbe and not searches:
                momentProbe = True
                found = self.recall.deliberate(utterance.words, person, conversation.focus.ids())
                events = [record for record in found if not record.isConstruct() or record.hitEpisode]
                self.searches.append(MemorySearch(self.probeWords.fill("probeMoment", WORDS=utterance.words[:70]),
                                                  len(events), len(found) - len(events)))
                self.associations.add(found)
                continue
            if not acts or self.hop >= hops + int(unknownProbe) + int(momentProbe):
                break
            self.goOn = False
            self.utterance = utterance
            self.reaction = reaction
            reaction.action.execute(self)
            if not self.goOn:
                break
        if kept is None:
            return TurnOutcome(failed=True)
        reaction, state, focusEntries, hereAndNow = kept
        affect = self._appraise(utterance, reaction, state, focusEntries, hereAndNow)
        valence, intensity = self.being.temperament.apply(affect.valence, affect.intensity)
        conversation.lastAssociations = self.associations.records()
        event = self.eventWords.said(person, utterance.words)
        if reaction.words:
            event = self.eventWords.replied(event, self.being.name, reaction.words)
        moment = Moment(person, event, reaction.retold, affect.feeling, affect.conclusion, valence, intensity,
                        self.clock.now())
        self._keep(moment)
        self._evoke()
        self._fold()
        return TurnOutcome(reaction.words, self.thoughts)

    # ---- acts of a turn ----

    def performSpeak(self, action):
        return

    def performStaySilent(self, action):
        return

    def performSearchMemory(self, action):
        found = self.recall.deliberate(action.query, self.conversation.person, self.conversation.focus.ids())
        self.searches.append(MemorySearch(action.query, len(found)))
        self.associations.add(found)
        self.goOn = True

    def performThink(self, action):
        """The chain starts from the moment as it stood: what was said, the reply the being was about
        to give, what it made of it, and the angle it wanted to think about. With introspection off
        (an ablation) the pause is not taken: the reply the being was about to give is the answer."""
        if not self.parameters["introspection"]:
            return
        event = self.eventWords.said(self.conversation.person, self.utterance.words)
        if self.reaction.words:
            event = self.eventWords.replied(event, self.being.name, self.reaction.words)
        self.thoughts += self.reflection.run(self.conversation.focus, self.conversation.person, event,
                                             self.reaction.conclusion, action.angle)
        self.goOn = True

    # ---- an arrival ----

    def onArrival(self, arrival):
        conversation = self.conversation
        person = arrival.person
        self.presence.enter(self.presenceKey, conversation.sessionId, person)
        self.presence.heartbeat(conversation.sessionId)
        self.slot.load(self.clock.now())
        self.associations = Associations()
        self.associations.add(self.recall.aboutPerson(person, self.parameters["arrivalAssociations"]))
        recent = self.hippocampus.mostRecentlyFelt(self.parameters["recentCount"], livedOnly=True)
        others = self.presence.others(self.presenceKey, conversation.sessionId)
        reaction = None
        for hop in range(self.parameters["turnActionHops"] + 1):
            state, focusEntries = self._compose(recent)
            senses = Senses(Hearing(Hearing.ARRIVAL, person),
                            AttentionAndMemory(len(state), len(self.associations), self.hippocampus.size()))
            hereAndNow = HereAndNow(self.clock.now(), self.being.name, person, others, senses)
            conversation.lastHereAndNow = hereAndNow
            context = ReplyContext(ReplyContext.ARRIVAL, hereAndNow, state, focusEntries, self.clock,
                                   self.feelingWords, self.fading, self.rumination, held=self._slotBlock(),
                                   lastDays=self._lastDays())
            reaction = self.responding.react(context)
            if reaction.failed or reaction.action.target is not ActionTarget.MEMORY:
                break
            if hop < self.parameters["turnActionHops"]:
                self.associations.add(self.recall.plain(reaction.action.query, person))
        conversation.lastAssociations = self.associations.records()
        greeting = "" if reaction is None or reaction.failed else reaction.words
        event = self.eventWords.entered(person)
        if greeting:
            event = self.eventWords.replied(event, self.being.name, greeting)
        now = self.clock.now()
        if reaction is not None and not reaction.failed:
            valence, intensity = self.being.temperament.apply(reaction.valence, reaction.intensity)
            arrivalRecord = EmoThought(EmoThought.newId(), self.being.id, Author.person(person), reaction.feeling,
                                       reaction.conclusion, valence, Strength(intensity, now), now)
            arrivalRecord.episodes = [Episode(Episode.newId(), self.being.id, arrivalRecord.id, person, event, now)]
            conversation.focus.pushMoment(arrivalRecord, now)
        self._evoke()
        self._fold()
        conversation.livingRecordId = None
        return TurnOutcome(greeting)

    # ---- a departure ----

    def onDeparture(self, departure):
        """No record and no reply. The context the being worked from, as it stands when the person
        leaves, is what disposition learning reads; first the being has its quiet. Last, the
        conversation is folded into today."""
        conversation = self.conversation
        person = departure.person
        self.slot.load(self.clock.now())
        self.associations = Associations()
        self.associations.add(self.recall.aboutPerson(person, self.parameters["arrivalAssociations"]))
        recent = self.hippocampus.mostRecentlyFelt(self.parameters["recentCount"], livedOnly=True)
        state, focusEntries = self._compose(recent)
        senses = Senses(Hearing(Hearing.DEPARTURE, person),
                        AttentionAndMemory(len(state), len(self.associations), self.hippocampus.size()))
        hereAndNow = HereAndNow(self.clock.now(), self.being.name, person,
                                self.presence.others(self.presenceKey, conversation.sessionId), senses)
        conversation.closingContext = ReplyContext(
            ReplyContext.DEPARTURE, hereAndNow, state, focusEntries, self.clock, self.feelingWords,
            self.fading, self.rumination, held=self._slotBlock(), summary=conversation.focus.summary,
            lastDays=self._lastDays()).render()
        self.presence.leave(conversation.sessionId)
        for _ in range(self.parameters["quietThoughts"]):
            self.thoughts += self.reflection.run(conversation.focus)
        self._learn(person)
        if self.lastDays is not None:
            self.lastDays.conversationEnded(conversation.focus)
        conversation.closed = True
        return TurnOutcome("", self.thoughts)

    # ---- helpers ----

    def _lastDays(self):
        """The last days as they stand, beside the focus in every reply context; None when the
        layer is switched off."""
        return None if self.lastDays is None else self.lastDays.current()

    def _applicable(self, person, words):
        if not self.selection.hasAny(self.being):
            return []
        moments = [entry for entry in self.conversation.focus.moments(person)
                   if any(self.eventWords.isSaid(episode.asItHappened) for episode in entry.record.episodes or [])]
        lines = [episode.text(Rendering.AS_IT_HAPPENED) for entry in moments[-2:]
                 for episode in entry.record.episodes or []]
        situation = Situation("\n".join(lines + [self.eventWords.said(person, words)]).strip())
        return self.selection.select(self.being, situation, self.carried.text())

    def _compose(self, recent):
        """The state from the recent records and the strongest associations, and the focus line for
        this turn. A felt record the being brought from elsewhere enters the line when it enters the
        state. What came to mind in this turn, strong or weak, stands at the end of the line. The
        being's own constructs are not felt: bringing one to mind puts it in the slot."""
        now = self.clock.now()
        felt = []
        for record in self.associations.records():
            if record.isConstruct():
                self.slot.activate(record, now)
            else:
                felt.append(record)
        state, _ = State.compose(recent, felt, now, self.fading, self.parameters["stateMassBudget"])
        self.hippocampus.withEpisodes(state.entries, self.parameters["episodesPerFeeling"], reload=True)
        focus = self.conversation.focus
        associationIds = {record.id for record in felt}
        for record in state.entries:
            if record.id not in associationIds:
                focus.pushCarried(record, now)
        current = [FocusEntry(record, FocusEntry.EVOKED_FROM_BEFORE, now)
                   for record in self.hippocampus.withEpisodes(felt, self.parameters["episodesPerFeeling"])]
        held = self.slot.heldSince() if self.parameters["heldThoughtsInLine"] else []
        return state, focus.line(current, held)

    def _slotBlock(self):
        """The held thoughts as their own block, when they are not placed in the focus line."""
        return [] if self.parameters["heldThoughtsInLine"] else self.slot.held()

    def _appraise(self, utterance, reaction, state, focusEntries, hereAndNow):
        associationIds = self.associations.ids()
        remembered = [record for record in state if record.id in associationIds]
        counts = hereAndNow.senses.attentionAndMemory
        senses = Senses(hereAndNow.senses.hearing,
                        AttentionAndMemory(counts.stateCount, counts.associationCount, counts.memoryCount,
                                           counts.searches, stateWithheld=True))
        context = AppraisalContext(
            HereAndNow(hereAndNow.now, hereAndNow.beingName, hereAndNow.person, hereAndNow.otherSessions, senses),
            remembered, focusEntries, self.clock, self.feelingWords, self.fading, self.rumination,
            utterance.words, summary=self.conversation.focus.summary)
        affect = self.appraisal.appraise(context)
        if affect is None:
            return Affect(reaction.feeling, reaction.conclusion, reaction.valence, reaction.intensity)
        return affect

    def _evoke(self):
        """What came to mind enters the focus line after the moment that evoked it."""
        now = self.clock.now()
        for record in self.associations.records():
            if record.isConstruct():
                self.slot.activate(record, now)
                continue
            self.hippocampus.withEpisodes([record], self.parameters["episodesPerFeeling"])
            self.conversation.focus.pushEvoked(record, now)

    def _fold(self):
        """What leaves view is folded into the summary, what was brought in from before apart from the
        conversation itself. If a call fails, its entries stay in view."""
        focus = self.conversation.focus
        leaving = focus.overflow()
        brought = [entry for entry in leaving if entry.isCarried()]
        lived = [entry for entry in leaving if not entry.isCarried()]
        if brought:
            text = self.summarising.fold(self.being.name, focus.summary.before, brought, before=True)
            if text is not None:
                focus.summary.before = text
                focus.fold(brought)
        if lived:
            text = self.summarising.fold(self.being.name, focus.summary.during, lived, before=False)
            if text is not None:
                focus.summary.during = text
                focus.fold(lived)

    def _keep(self, moment):
        encoded = self.encoding.encode(self.being.id, moment, self.conversation.livingRecordId,
                                       self.associations.records())
        if encoded.restores is not None:
            self.reconsolidation.restore(encoded.restores, moment.intensity)
        if encoded.isNew:
            self.conversation.livingRecordId = encoded.record.id
        record = EmoThought(encoded.record.id, self.being.id, Author.person(moment.person), moment.feeling,
                            moment.conclusion, moment.valence, Strength(moment.intensity, moment.at), moment.at)
        record.episodes = [encoded.episode]
        self.conversation.focus.pushMoment(record, moment.at)

    def _learn(self, person):
        moments = [entry.record for entry in self.conversation.focus.moments(person)
                   if any(self.eventWords.isSaid(episode.asItHappened) for episode in entry.record.episodes or [])]
        if len(moments) < 2:
            return
        peak = max(moments, key=lambda record: abs(record.valence))
        self.learning.learn(self.being, self.conversation.closingContext, self.carried.text(),
                            peak.valence or 0.1)

    @staticmethod
    def _kindProbe(kind):
        return "probe" + kind[0].upper() + kind[1:]
