from emostack.episode.Rendering import Rendering


class serviceBeingMemory:
    """What a being holds, for its owner to read: its records with their events, what it holds in
    mind, and what it has learned."""

    def __init__(self, engine):
        self.engine = engine

    def read(self, beingId):
        being = self.engine.beings.get(beingId)
        if being is None:
            raise ValueError("no such being")
        assembly = self.engine.assemblyFor(being)
        records = assembly.hippocampus.withEpisodes(assembly.hippocampus.all(), 20)
        slot = assembly.slot
        slot.load(self.engine.time.now())
        return {
            "being": being,
            "records": [{
                "kind": record.kind if record.isConstruct() else ("given" if record.isGiven() else "lived"),
                "text": record.statement() if record.isConstruct() else "",
                "feeling": record.feeling, "conclusion": record.conclusion, "valence": record.valence,
                "intensity": record.intensity, "happenedAt": record.happenedAt,
                "person": record.author.name,
                "events": [episode.text(Rendering.RETOLD) for episode in
                           sorted(record.episodes or [], key=lambda episode: episode.happenedAt)],
            } for record in records],
            "held": [construct.statement() for construct in slot.held()],
            "dispositions": [{"rule": d.rule, "weight": d.weight, "count": d.count}
                             for d in self.engine.repositories["dispositions"].strongestFirst(beingId, 200)],
        }
