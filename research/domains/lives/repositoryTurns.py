import json
import time


class repositoryTurns:
    """What happened in a run, in order, with every call to an LLM model in full: what the visitor
    said, what the being said, the events of arrival, departure and night, the thoughts the being
    formed, and what it was given at birth."""

    schema = [
        """CREATE TABLE IF NOT EXISTS turns (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             runId INTEGER NOT NULL,
             dayIndex INTEGER NOT NULL,
             roleId INTEGER,
             person TEXT NOT NULL DEFAULT '',
             turnIndex INTEGER NOT NULL DEFAULT 0,
             speaker TEXT NOT NULL,
             text TEXT NOT NULL DEFAULT '',
             valence REAL,
             intensity REAL,
             feeling TEXT NOT NULL DEFAULT '',
             calls TEXT NOT NULL DEFAULT '[]',
             at REAL NOT NULL
           )""",
        "CREATE INDEX IF NOT EXISTS turnsOfRun ON turns(runId, id)",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("turns", self.schema)

    def add(self, runId, dayIndex, speaker, text, person="", roleId=None, turnIndex=0, valence=None,
            intensity=None, feeling="", calls=None):
        cursor = self.database.write(
            "INSERT INTO turns (runId, dayIndex, roleId, person, turnIndex, speaker, text, valence, intensity, "
            "feeling, calls, at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (runId, dayIndex, roleId, person, turnIndex, speaker, text, valence, intensity, feeling,
             json.dumps(calls or [], ensure_ascii=False), time.time()))
        return cursor.lastrowid

    def forRun(self, runId, withCalls=True):
        rows = self.database.read("SELECT * FROM turns WHERE runId = ? ORDER BY id", (runId,))
        turns = []
        for row in rows:
            turn = dict(row)
            turn["calls"] = json.loads(turn["calls"] or "[]") if withCalls else []
            turns.append(turn)
        return turns
