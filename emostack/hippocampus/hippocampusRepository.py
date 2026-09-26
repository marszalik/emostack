import json
import re

from emostack.construct.constructFactory import constructFactory
from emostack.emoThought.Author import Author
from emostack.emoThought.EmoThought import EmoThought
from emostack.emoThought.Origin import Origin
from emostack.emoThought.Strength import Strength
from emostack.episode.Episode import Episode


class hippocampusRepository:
    """Records and episodes in SQLite. A record row is an emo-thought (type 'emoThought') or a
    cognitive construct (type = its kind)."""

    livedType = "emoThought"

    schema = [
        """CREATE TABLE IF NOT EXISTS records (
             id TEXT PRIMARY KEY,
             beingId INTEGER NOT NULL,
             type TEXT NOT NULL,
             authorKind TEXT NOT NULL,
             authorName TEXT NOT NULL DEFAULT '',
             origin TEXT NOT NULL DEFAULT 'lived',
             feeling TEXT NOT NULL DEFAULT '',
             conclusion TEXT NOT NULL DEFAULT '',
             text TEXT NOT NULL DEFAULT '',
             valence REAL NOT NULL,
             intensity REAL NOT NULL,
             happenedAt REAL NOT NULL,
             lastFelt REAL NOT NULL,
             vector TEXT NOT NULL DEFAULT '[]',
             originEpisodeId TEXT NOT NULL DEFAULT ''
           )""",
        "CREATE INDEX IF NOT EXISTS recordsOfBeing ON records(beingId, lastFelt DESC)",
        """CREATE TABLE IF NOT EXISTS episodes (
             id TEXT PRIMARY KEY,
             beingId INTEGER NOT NULL,
             recordId TEXT NOT NULL,
             person TEXT NOT NULL DEFAULT '',
             asItHappened TEXT NOT NULL,
             retold TEXT NOT NULL DEFAULT '',
             happenedAt REAL NOT NULL,
             vector TEXT NOT NULL DEFAULT '[]'
           )""",
        "CREATE INDEX IF NOT EXISTS episodesOfRecord ON episodes(recordId)",
        "CREATE INDEX IF NOT EXISTS episodesOfBeing ON episodes(beingId, happenedAt DESC)",
    ]

    def __init__(self, database):
        self.database = database
        self.constructs = constructFactory()
        database.ensureSchema("hippocampus", self.schema)

    # ---- writing ----

    def saveRecord(self, record):
        isConstruct = record.isConstruct()
        self.database.write(
            "INSERT INTO records (id, beingId, type, authorKind, authorName, origin, feeling, conclusion, text, "
            "valence, intensity, happenedAt, lastFelt, vector, originEpisodeId) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (record.id, record.beingId, record.kind if isConstruct else self.livedType,
             record.author.kind, record.author.name, record.origin.value, record.feeling,
             record.conclusion, record.text if isConstruct else "", record.valence,
             record.intensity, record.happenedAt, record.lastFelt, json.dumps(record.vector),
             "" if isConstruct else record.originEpisodeId))

    def saveEpisode(self, episode):
        self.database.write(
            "INSERT INTO episodes (id, beingId, recordId, person, asItHappened, retold, happenedAt, vector) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (episode.id, episode.beingId, episode.recordId, episode.person, episode.asItHappened,
             episode.retold, episode.happenedAt, json.dumps(episode.vector)))

    def setOriginEpisode(self, recordId, episodeId):
        self.database.write("UPDATE records SET originEpisodeId = ? WHERE id = ?", (episodeId, recordId))

    def setStrength(self, recordId, intensity, lastFelt):
        self.database.write("UPDATE records SET intensity = ?, lastFelt = ? WHERE id = ?",
                            (float(intensity), float(lastFelt), recordId))

    def setIntensity(self, recordId, intensity):
        self.database.write("UPDATE records SET intensity = ? WHERE id = ?", (float(intensity), recordId))

    def moveEpisodes(self, fromRecordId, toRecordId):
        cursor = self.database.write("UPDATE episodes SET recordId = ? WHERE recordId = ?",
                                     (toRecordId, fromRecordId))
        return cursor.rowcount

    def delete(self, recordId):
        self.database.writeMany([("DELETE FROM episodes WHERE recordId = ?", (recordId,)),
                                 ("DELETE FROM records WHERE id = ?", (recordId,))])

    def deleteBeing(self, beingId):
        self.database.writeMany([("DELETE FROM episodes WHERE beingId = ?", (beingId,)),
                                 ("DELETE FROM records WHERE beingId = ?", (beingId,))])

    # ---- reading ----

    def record(self, recordId):
        row = self.database.readOne("SELECT * FROM records WHERE id = ?", (recordId,))
        return self._record(row) if row else None

    def all(self, beingId):
        rows = self.database.read("SELECT * FROM records WHERE beingId = ? ORDER BY lastFelt DESC", (beingId,))
        return [self._record(row) for row in rows]

    def count(self, beingId):
        return self.database.readOne("SELECT COUNT(*) FROM records WHERE beingId = ?", (beingId,))[0]

    def mostRecentlyFelt(self, beingId, limit, livedOnly=False):
        where = "beingId = ?" + (" AND type = ?" if livedOnly else "")
        parameters = (beingId, self.livedType, limit) if livedOnly else (beingId, limit)
        rows = self.database.read(f"SELECT * FROM records WHERE {where} ORDER BY lastFelt DESC LIMIT ?",
                                  parameters)
        return [self._record(row) for row in rows]

    def constructsOfKind(self, beingId, kind):
        rows = self.database.read("SELECT * FROM records WHERE beingId = ? AND type = ? ORDER BY lastFelt DESC",
                                  (beingId, kind))
        return [self._record(row) for row in rows]

    def episodesOf(self, recordId, limit):
        rows = self.database.read(
            "SELECT * FROM episodes WHERE recordId = ? ORDER BY happenedAt DESC LIMIT ?", (recordId, limit))
        return [self._episode(row) for row in rows]

    def searchableEpisodes(self, beingId):
        rows = self.database.read("SELECT * FROM episodes WHERE beingId = ? AND vector != '[]'", (beingId,))
        return [self._episode(row) for row in rows]

    def recordIdsMentioning(self, beingId, names):
        """Records lived with one of these people, or whose events (either rendering) or text
        mention one of them as a whole word."""
        names = [name for name in names if name]
        if not names:
            return set()
        pattern = re.compile(r"\b(" + "|".join(re.escape(name) for name in set(names)) + r")\b", re.I)
        lowered = {name.lower() for name in names}
        found = set()
        for row in self.database.read(
                "SELECT recordId, person, asItHappened, retold FROM episodes WHERE beingId = ?", (beingId,)):
            if (row["person"] or "").lower() in lowered or pattern.search(f"{row['asItHappened']} {row['retold']}"):
                found.add(row["recordId"])
        for row in self.database.read(
                "SELECT id, authorName, text, conclusion FROM records WHERE beingId = ?", (beingId,)):
            if (row["authorName"] or "").lower() in lowered or pattern.search(f"{row['text']} {row['conclusion']}"):
                found.add(row["id"])
        return found

    def _record(self, row):
        strength = Strength(row["intensity"], row["lastFelt"])
        vector = json.loads(row["vector"] or "[]")
        if row["type"] == self.livedType:
            return EmoThought(row["id"], row["beingId"], Author(row["authorKind"], row["authorName"]),
                              row["feeling"], row["conclusion"], row["valence"], strength,
                              row["happenedAt"], Origin(row["origin"]), vector, row["originEpisodeId"])
        return self.constructs.create(
            row["type"], id=row["id"], beingId=row["beingId"], text=row["text"], feeling=row["feeling"],
            conclusion=row["conclusion"], valence=row["valence"], strength=strength,
            happenedAt=row["happenedAt"], vector=vector)

    @staticmethod
    def _episode(row):
        return Episode(row["id"], row["beingId"], row["recordId"], row["person"], row["asItHappened"],
                       row["happenedAt"], row["retold"], json.loads(row["vector"] or "[]"))
