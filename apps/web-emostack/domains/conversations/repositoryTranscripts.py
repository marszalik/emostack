import json
import time


class repositoryTranscripts:
    """What was said in a being's conversations, kept in the owner's own store, so that they can be
    read again: who said what, the being's silences and thoughts, arrivals and departures."""

    schema = [
        """CREATE TABLE IF NOT EXISTS transcripts (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             beingId INTEGER NOT NULL,
             conversationId TEXT NOT NULL,
             person TEXT NOT NULL,
             role TEXT NOT NULL,
             text TEXT NOT NULL,
             details TEXT NOT NULL DEFAULT '{}',
             at REAL NOT NULL
           )""",
        "CREATE INDEX IF NOT EXISTS transcriptsOfBeing ON transcripts(beingId, conversationId)",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("transcripts", self.schema)

    def add(self, beingId, conversationId, person, role, text, details=None):
        self.database.write(
            "INSERT INTO transcripts (beingId, conversationId, person, role, text, details, at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (beingId, conversationId, person, role, text, json.dumps(details or {}, ensure_ascii=False), time.time()))

    def conversations(self, beingId):
        rows = self.database.read(
            "SELECT conversationId, person, MIN(at) AS startedAt, COUNT(*) AS lines FROM transcripts "
            "WHERE beingId = ? GROUP BY conversationId ORDER BY startedAt DESC", (beingId,))
        return [dict(row) for row in rows]

    def conversation(self, beingId, conversationId):
        rows = self.database.read("SELECT * FROM transcripts WHERE beingId = ? AND conversationId = ? ORDER BY id",
                                  (beingId, conversationId))
        return [dict(row, details=json.loads(row["details"] or "{}")) for row in rows]
