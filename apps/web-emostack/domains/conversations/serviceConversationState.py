from emostack.containers.State import State
from emostack.episode.Rendering import Rendering


class serviceConversationState:
    """What is inside the being during a conversation, for the right-hand column, container by
    container in the order the reply reads them: here and now, with the senses as the last reply
    read them; the
    state, marking what the last words brought to mind; the accessibility slot; the conversation
    summary; the dispositions applied to the last reply; and the focus as the reply reads it, where
    the associations that did not fit in the state stay in view."""

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
        evokedIds = {record.id for record in associations}
        key = (engine.database.path, being.id)
        return {
            "now": now,
            "awake": being.isAwake(),
            "person": live.person,
            "senses": self._senses(conversation),
            "others": sorted({session.person for session in engine.presence.others(key, conversation.sessionId if conversation else None)}),
            "held": [{"text": construct.statement(), "at": construct.happenedAt} for construct in assembly.slot.held()],
            "state": [dict(self._record(record, now, assembly.fadingLaw), evoked=record.id in evokedIds)
                      for record in state],
            "summary": (conversation.summary.text or "").strip() if conversation else "",
            "focus": [dict(self._record(entry.record, now, assembly.fadingLaw, entry.isEvoked()), evoked=entry.isEvoked())
                      for entry in (conversation.focus.entries if conversation else [])
                      if not (entry.isEvoked() and entry.record.id in state.ids())],
            "dispositions": [{"rule": d.rule, "weight": d.weight, "count": d.count}
                             for d in (conversation.lastDispositions if conversation else [])],
        }

    @staticmethod
    def _senses(conversation):
        hereAndNow = conversation.lastHereAndNow if conversation else None
        if hereAndNow is None:
            return []
        return [line.strip() for line in hereAndNow.senses.render().splitlines()
                if line.strip() and not line.startswith("===")]

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
