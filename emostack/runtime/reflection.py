from emostack.processes.introspection.IntrospectionContext import IntrospectionContext


class reflection:
    """The slow path. Introspection forms one thought; its act may continue the chain, by thinking
    once more or by searching memory, or end it by forming a construct. What the slow path produces
    does not go back into the felt state: it goes into the accessibility slot, where the fast path
    reads it."""

    def __init__(self, being, hippocampus, slot, introspection, formation, reconsolidation, recall,
                 clock, feelingWords, entries=8, maxSteps=3, episodesPerEntry=5):
        self.being = being
        self.hippocampus = hippocampus
        self.slot = slot
        self.introspection = introspection
        self.formation = formation
        self.reconsolidation = reconsolidation
        self.recall = recall
        self.clock = clock
        self.feelingWords = feelingWords
        self.entryCount = entries
        self.maxSteps = maxSteps
        self.episodesPerEntry = episodesPerEntry

    def run(self, focus=None, person=None, momentText=None, momentConclusion="", intent=""):
        """In the quiet nothing but the focus is given. Mid-turn, `person` is who the being is talking
        with, and the chain starts from the moment the being stopped at: the exchange as it stood
        (`momentText`), what it made of it, and what it wanted to think about (`intent`). Returns the
        thoughts and constructs formed."""
        if not self.slot.loaded:
            self.slot.load(self.clock.now())
        self.formed = []
        self.previous = (momentText, momentConclusion) if momentText is not None else None
        self.direction = intent
        self.recalled = None
        for self.depth in range(self.maxSteps + 1):
            now = self.clock.now()
            context = IntrospectionContext(
                self.being.name, now, self._entries(focus), self.clock, self.feelingWords, person=person,
                previous=self.previous, direction=self.direction, recalled=self.recalled)
            self.step = self.introspection.reflect(context, self.being.temperament)
            if self.step is None:
                break
            thought = self._keepThought(now)
            self.goOn = False
            self.step.action.execute(self)
            if not self.goOn:
                break
            self.previous = (thought.text, thought.conclusion)
        return self.formed

    # ---- acts of reflection ----

    def performKeepThinking(self, action):
        """The being thinks once more. The next step is told only that it chose to keep thinking."""
        if self.depth < self.maxSteps:
            self.direction = ""
            self.recalled = None
            self.goOn = True

    def performSearchMemory(self, action):
        if self.depth < self.maxSteps:
            self.direction = action.query
            self.recalled = self.hippocampus.withEpisodes(self.recall.plain(action.query), self.episodesPerEntry)
            self.goOn = True

    def performFormConstruct(self, action):
        construct = self.formation.keepConstruct(self.being.id, action.kind, action.text, self.step)
        self.slot.activate(construct, self.clock.now())
        self.formed.append(construct)

    def performDoNothing(self, action):
        return

    # ---- helpers ----

    def _keepThought(self, now):
        thought, recurrence = self.formation.keepThought(self.being.id, self.step)
        if recurrence:
            self.reconsolidation.restore(thought, self.step.intensity)
        elif self.step.reinforcesId:
            target = self.hippocampus.record(self.step.reinforcesId)
            if target is not None and target.sameSign(self.step.valence):
                self.reconsolidation.restore(target, self.step.intensity)
        self.slot.activate(thought, now)
        self.formed.append(thought)
        return thought

    def _entries(self, focus):
        """The slot first; then the tail of the focus filled up with the most recently felt records,
        most recent first, without the being's own constructs, which the slot holds."""
        tail = [entry.record for entry in (focus.entries if focus else [])][-self.entryCount:]
        tailIds = {record.id for record in tail}
        room = self.entryCount - len(tail)
        extras = []
        if room > 0:
            extras = [record for record in self.hippocampus.mostRecentlyFelt(self.entryCount)
                      if record.id not in tailIds][:room]
        entries = sorted(tail + extras, key=lambda record: record.lastFelt, reverse=True)
        self.hippocampus.withEpisodes(entries, self.episodesPerEntry)
        held = self.slot.held()
        heldIds = {construct.id for construct in held}
        return held + [record for record in entries if not record.isConstruct() and record.id not in heldIds]
