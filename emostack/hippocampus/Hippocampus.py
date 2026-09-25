class Hippocampus:
    """Everything one being has lived: its emo-thoughts with their episodes and its constructs.
    Every record is written once, as it happens, and thinned only in sleep."""

    def __init__(self, beingId, repository):
        self.beingId = beingId
        self.repository = repository

    def keep(self, record):
        self.repository.saveRecord(record)

    def keepEpisode(self, episode):
        self.repository.saveEpisode(episode)

    def record(self, recordId):
        return self.repository.record(recordId)

    def all(self):
        return self.repository.all(self.beingId)

    def size(self):
        return self.repository.count(self.beingId)

    def mostRecentlyFelt(self, limit, livedOnly=False):
        return self.repository.mostRecentlyFelt(self.beingId, limit, livedOnly)

    def constructsOfKind(self, kind):
        return self.repository.constructsOfKind(self.beingId, kind)

    def searchableEpisodes(self):
        return self.repository.searchableEpisodes(self.beingId)

    def mentioning(self, names):
        return self.repository.recordIdsMentioning(self.beingId, names)

    def setStrength(self, record, intensity, lastFelt):
        record.strength.intensity = float(intensity)
        record.strength.lastFelt = float(lastFelt)
        self.repository.setStrength(record.id, intensity, lastFelt)

    def setIntensity(self, record, intensity):
        record.strength.intensity = float(intensity)
        self.repository.setIntensity(record.id, intensity)

    def setOriginEpisode(self, record, episode):
        record.originEpisodeId = episode.id
        self.repository.setOriginEpisode(record.id, episode.id)

    def moveEpisodes(self, fromRecord, toRecord):
        return self.repository.moveEpisodes(fromRecord.id, toRecord.id)

    def forget(self, record):
        self.repository.delete(record.id)

    def withEpisodes(self, records, limit, reload=False):
        """Loads the episodes of lived records that have none loaded yet, newest first; the episode
        that brought a record into recall goes first. A construct has no episodes."""
        for record in records:
            if record.isConstruct() or (record.episodes is not None and not reload):
                continue
            record.episodes = self.repository.episodesOf(record.id, limit)
            hit = record.hitEpisode
            if hit is not None and all(episode.id != hit.id for episode in record.episodes):
                record.episodes = [hit] + record.episodes[:max(0, limit - 1)]
        return records
