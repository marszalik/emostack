class serviceListBeings:
    """A person's beings as the home page shows them: how much they hold, whether they are awake,
    what they felt last, and who is talking with them now."""

    def __init__(self, engine):
        self.engine = engine

    def list(self):
        beings = []
        for being in self.engine.beings.all():
            assembly = self.engine.assemblyFor(being)
            last = assembly.hippocampus.mostRecentlyFelt(1, livedOnly=True)
            key = (self.engine.database.path, being.id)
            beings.append({
                "id": being.id, "name": being.name, "awake": being.isAwake(),
                "records": assembly.hippocampus.size(),
                "mood": {"valence": last[0].valence, "intensity": last[0].intensity,
                         "feeling": last[0].feeling[:60]} if last else None,
                "talking": sorted({session.person for session in self.engine.presence.others(key, None)}),
                "temperament": being.temperament.toDict(),
            })
        return beings
