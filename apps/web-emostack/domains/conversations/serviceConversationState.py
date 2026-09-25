from emostack.containers.State import State
from emostack.episode.Rendering import Rendering


class serviceConversationState:
    """What is inside the being during a conversation, for the right-hand column: what it holds in
    mind, what it feels now, this conversation as it attends to it, what came to mind last, and
    what it has learned."""

    def state(self, live):
        engine = live.engine
        being = engine.beings.get(live.beingId)
        assembly = engine.assemblyFor(being)
        now = engine.time.now()
        assembly.slot.load(now)
        recent = assembly.hippocampus.mostRecentlyFelt(engine.parameters["recentCount"], livedOnly=True)
        conversation = live.conversation
        associations = [record for record in (conversation.lastAssociations if conversation else [])
                        if not record.isConstruct()]
        state, _ = State.compose(recent, associations, now, assembly.fadingLaw, engine.parameters["stateMassBudget"])
        assembly.hippocampus.withEpisodes(state.entries, 3)
        key = (engine.database.path, being.id)
        return {
            "now": now,
            "awake": being.isAwake(),
            "others": sorted({session.person for session in engine.presence.others(key, conversation.sessionId if conversation else None)}),
            "held": [{"text": construct.statement(), "at": construct.happenedAt} for construct in assembly.slot.held()],
            "state": [self._record(record, now, assembly.fadingLaw) for record in state],
            "focus": [self._record(entry.record, now, assembly.fadingLaw, entry.isEvoked())
                      for entry in (conversation.focus.entries if conversation else [])],
            "associations": [self._record(record, now, assembly.fadingLaw, True)
                             for record in (conversation.lastAssociations if conversation else [])],
            "dispositions": [{"rule": d.rule, "weight": d.weight, "count": d.count}
                             for d in engine.repositories["dispositions"].strongestFirst(being.id, 100)],
        }

    @staticmethod
    def _record(record, now, fading, retold=False):
        if record.isConstruct():
            event = record.statement()
        else:
            rendering = Rendering.RETOLD if retold else Rendering.AS_IT_HAPPENED
            episodes = sorted(record.episodes or [], key=lambda episode: episode.happenedAt)
            event = " / ".join(episode.text(rendering) for episode in episodes)
        return {"feeling": record.feeling, "event": event, "conclusion": record.conclusion,
                "valence": record.valence, "felt": record.feltAt(now, fading), "at": record.happenedAt}
