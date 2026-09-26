from emostack.being.Temperament import Temperament
from emostack.emoThought.Author import Author
from emostack.emoThought.EmoThought import EmoThought
from emostack.emoThought.Origin import Origin
from emostack.emoThought.Strength import Strength
from emostack.episode.Episode import Episode
from emostack.being.beingRepository import beingRepository
from emostack.containers.accessibilitySlotRepository import accessibilitySlotRepository
from emostack.core.database import database
from emostack.core.localEmbedder import localEmbedder
from emostack.core.openAiCompatibleProcessor import openAiCompatibleProcessor
from emostack.core.timeSource import timeSource
from emostack.disposition.dispositionRepository import dispositionRepository
from emostack.hippocampus.hippocampusRepository import hippocampusRepository
from emostack.runtime.Conversation import Conversation
from emostack.runtime.assembly import assembly
from emostack.runtime.clock import clock
from emostack.runtime.presence import presence
from emostack.trigger.Arrival import Arrival
from emostack.trigger.Departure import Departure
from emostack.trigger.Utterance import Utterance


class engine:
    """The way in for an application: open a conversation with a being, let a person speak, let
    them leave, and let time pass."""

    def __init__(self, settings, processor=None, embedder=None, time=None):
        self.settings = settings
        self.parameters = settings.section("parameters")
        self.processor = processor or openAiCompatibleProcessor(settings.section("processor"))
        self.embedder = embedder or localEmbedder(settings.section("embedder"))
        self.time = time or timeSource()
        self.database = database(settings.databasePath)
        self.beings = beingRepository(self.database)
        self.repositories = {
            "hippocampus": hippocampusRepository(self.database),
            "dispositions": dispositionRepository(self.database),
            "slot": accessibilitySlotRepository(self.database),
        }
        self.presence = presence(self.time, self.parameters["presenceStaleSeconds"])
        self.clock = clock(self.beings, self.assemblyFor, self.time, self.parameters)

    def being(self, name, temperament=None):
        """The being of this name; created, with the configured temperament, if it does not exist."""
        found = self.beings.named(name)
        if found is not None:
            return found
        return self.beings.create(name, temperament or Temperament.fromDict(self.settings.section("temperament")),
                                  self.time.now())

    def assemblyFor(self, being):
        return assembly(being, self.repositories, self.processor, self.embedder, self.time, self.presence,
                        (self.database.path, being.id), self.parameters)

    def open(self, beingName, person):
        """A person arrives. Returns the conversation and what the being said, if it greeted."""
        being = self.being(beingName)
        self._activity(being)
        conversation = Conversation(being, person, self.time.now(), self.parameters["focusCap"],
                                    self.parameters["summaryEveryTurns"])
        outcome = self.assemblyFor(being).turnFor(conversation).take(Arrival(person, self.time.now()))
        return conversation, outcome

    def hear(self, conversation, words):
        self._activity(conversation.being)
        return self.assemblyFor(conversation.being).turnFor(conversation).take(
            Utterance(conversation.person, words, self.time.now()))

    def leave(self, conversation):
        self._activity(conversation.being)
        return self.assemblyFor(conversation.being).turnFor(conversation).take(
            Departure(conversation.person, self.time.now()))

    def remember(self, beingName, event, feeling, conclusion, valence, intensity, ageHours=0.0):
        """A record given at birth: lived as far as the being can tell, but never folded away in
        sleep and never forgotten. Returns the record."""
        being = self.being(beingName)
        at = self.time.now() - float(ageHours) * 3600.0
        record = EmoThought(EmoThought.newId(), being.id, Author.itself(), feeling, conclusion, valence,
                            Strength(intensity, at), at, Origin.GIVEN)
        record.vector = self.embedder.embed(record.embeddingText()) if record.embeddingText() else []
        hippocampus = self.assemblyFor(being).hippocampus
        hippocampus.keep(record)
        episode = Episode(Episode.newId(), being.id, record.id, "", event, at, "", self.embedder.embed(event))
        hippocampus.keepEpisode(episode)
        hippocampus.setOriginEpisode(record, episode)
        return record

    def night(self, beingName, consolidate=False):
        """Sleep now, whatever the clock says: fold the awake period if asked, then forget what is
        too weak for its age. Returns the number of records forgotten."""
        being = self.being(beingName)
        sleep = self.assemblyFor(being).sleep()
        if consolidate:
            sleep.consolidate(being, being.wokeAt or 0.0)
        return len(sleep.forget())

    def think(self, conversation):
        """The being stops to think now, in the middle of a conversation, with nobody asking.
        Returns the thoughts and constructs formed."""
        self._activity(conversation.being)
        return self.assemblyFor(conversation.being).reflection().run(conversation.focus)

    def deleteBeing(self, beingId):
        """The being and everything it has lived."""
        self.repositories["hippocampus"].deleteBeing(beingId)
        self.repositories["dispositions"].deleteBeing(beingId)
        self.repositories["slot"].replace(beingId, [])
        self.beings.delete(beingId)

    def copyBeing(self, sourcePath, sourceBeingId, name):
        """A copy of a being that has lived, from another store, with all its records, episodes,
        dispositions and slot; the source is untouched. Returns the new being."""
        connection = self.database.connection
        with self.database.lock:
            connection.execute("ATTACH DATABASE ? AS source", (sourcePath,))
            try:
                row = connection.execute("SELECT * FROM source.beings WHERE id = ?", (sourceBeingId,)).fetchone()
                if row is None:
                    raise ValueError("no such being in the source")
                cursor = connection.execute(
                    "INSERT INTO beings (name, createdAt, valenceBias, intensityAmplification, avoidanceWeight) "
                    "VALUES (?, ?, ?, ?, ?)", (name, self.time.now(), row["valenceBias"], row["intensityAmplification"],
                                               row["avoidanceWeight"]))
                newId = cursor.lastrowid
                suffix = f"-c{newId}"
                connection.execute(
                    "INSERT INTO records SELECT id || ?, ?, type, authorKind, authorName, origin, feeling, conclusion, "
                    "text, valence, intensity, happenedAt, lastFelt, vector, CASE WHEN originEpisodeId = '' THEN '' "
                    "ELSE originEpisodeId || ? END FROM source.records WHERE beingId = ?",
                    (suffix, newId, suffix, sourceBeingId))
                connection.execute(
                    "INSERT INTO episodes SELECT id || ?, ?, recordId || ?, person, asItHappened, retold, happenedAt, "
                    "vector FROM source.episodes WHERE beingId = ?", (suffix, newId, suffix, sourceBeingId))
                connection.execute(
                    "INSERT INTO dispositions (beingId, rule, weight, count, updatedAt) SELECT ?, rule, weight, count, "
                    "updatedAt FROM source.dispositions WHERE beingId = ?", (newId, sourceBeingId))
                connection.execute(
                    "INSERT INTO slot SELECT ?, recordId || ?, activatedAt FROM source.slot WHERE beingId = ?",
                    (newId, suffix, sourceBeingId))
                connection.commit()
            finally:
                connection.execute("DETACH DATABASE source")
        return self.beings.get(newId)

    def tick(self):
        self.clock.tick()

    def close(self):
        self.database.close()

    def _activity(self, being):
        being.wake(self.time.now())
        self.beings.saveWakefulness(being)
