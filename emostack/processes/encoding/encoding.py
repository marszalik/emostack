from emostack.emoThought.EmoThought import EmoThought
from emostack.episode.Episode import Episode
from emostack.processes.encoding.Encoding import Encoding


class encoding:
    """Persistence of a moment. Within a conversation, a moment whose feeling has the same sign as
    the record being lived joins it as another episode and restores its strength; a change of sign
    opens a new record. Otherwise the moment forms a record of its own, with the moment as its
    first episode, and the strongest lived memory of the same sign that this turn brought to mind
    comes back: it regains strength, but it does not take the event. Being mocked for a loss is not
    a recurrence of the grief; filed under the old memory, the new blow would read as the old
    sadness."""

    def __init__(self, hippocampus, embedder):
        self.hippocampus = hippocampus
        self.embedder = embedder

    def encode(self, beingId, moment, livingRecordId, associations):
        eventVector = self.embedder.embed(moment.event) if moment.event.strip() else []
        living = self.hippocampus.record(livingRecordId) if livingRecordId else None
        if living is not None and living.sameSign(moment.valence):
            return Encoding(living, self._episode(beingId, living, moment, eventVector), living, isNew=False)
        recalled = self._recalled(moment, associations)
        record = EmoThought.lived(beingId, moment.person, moment.feeling, moment.conclusion,
                                  moment.valence, moment.intensity, moment.at)
        record.vector = self.embedder.embed(record.embeddingText()) if record.embeddingText() else []
        self.hippocampus.keep(record)
        episode = self._episode(beingId, record, moment, eventVector)
        self.hippocampus.setOriginEpisode(record, episode)
        return Encoding(record, episode, recalled, isNew=True)

    def _recalled(self, moment, associations):
        best = None
        for association in associations:
            if association.isConstruct():
                continue
            record = self.hippocampus.record(association.id)
            if record is None or not record.sameSign(moment.valence):
                continue
            if best is None or record.intensity > best.intensity:
                best = record
        return best

    def _episode(self, beingId, record, moment, vector):
        episode = Episode(Episode.newId(), beingId, record.id, moment.person, moment.event, moment.at,
                          moment.retold, vector)
        self.hippocampus.keepEpisode(episode)
        record.episodes = [episode]
        return episode
