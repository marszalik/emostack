import json
import time


class repositoryRuns:
    """Runs: one life of one arm of a scenario, and everything it was run with."""

    schema = [
        """CREATE TABLE IF NOT EXISTS runs (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             scenarioId INTEGER NOT NULL,
             experimentId INTEGER,
             armLabel TEXT NOT NULL DEFAULT '',
             arm TEXT NOT NULL DEFAULT 'sheep',
             iteration INTEGER NOT NULL DEFAULT 0,
             status TEXT NOT NULL DEFAULT 'queued',
             sheepModelId INTEGER,
             visitorModelId INTEGER,
             embedModelId INTEGER,
             settings TEXT NOT NULL DEFAULT '{}',
             storePath TEXT NOT NULL DEFAULT '',
             error TEXT NOT NULL DEFAULT '',
             createdAt REAL NOT NULL,
             finishedAt REAL
           )""",
        "CREATE INDEX IF NOT EXISTS runsOfExperiment ON runs(experimentId)",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("runs", self.schema)

    def create(self, scenarioId, arm, sheepModelId, visitorModelId, embedModelId, experimentId=None,
               armLabel="", iteration=0, settings=None):
        cursor = self.database.write(
            "INSERT INTO runs (scenarioId, experimentId, armLabel, arm, iteration, sheepModelId, visitorModelId, "
            "embedModelId, settings, createdAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (scenarioId, experimentId, armLabel, arm, iteration, sheepModelId, visitorModelId, embedModelId,
             json.dumps(settings or {}, ensure_ascii=False), time.time()))
        return cursor.lastrowid

    def get(self, runId):
        row = self.database.readOne("SELECT * FROM runs WHERE id = ?", (runId,))
        return self._run(row) if row else None

    def recent(self, limit=200):
        return [self._run(row) for row in self.database.read("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))]

    def forExperiment(self, experimentId):
        return [self._run(row) for row in self.database.read(
            "SELECT * FROM runs WHERE experimentId = ? ORDER BY iteration, armLabel", (experimentId,))]

    def setStatus(self, runId, status, error=""):
        finished = time.time() if status in ("done", "error", "stopped") else None
        self.database.write("UPDATE runs SET status = ?, error = ?, finishedAt = ? WHERE id = ?",
                            (status, error, finished, runId))

    def setSettings(self, runId, settings, storePath=""):
        self.database.write("UPDATE runs SET settings = ?, storePath = ? WHERE id = ?",
                            (json.dumps(settings, ensure_ascii=False), storePath, runId))

    def delete(self, runId):
        self.database.writeMany([("DELETE FROM turns WHERE runId = ?", (runId,)),
                                 ("DELETE FROM runs WHERE id = ?", (runId,))])

    @staticmethod
    def _run(row):
        run = dict(row)
        run["settings"] = json.loads(run["settings"] or "{}")
        return run
