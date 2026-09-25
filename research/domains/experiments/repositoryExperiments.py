import json
import time


class repositoryExperiments:
    """Experiments: a scenario run in several arms, each repeated, with the same models."""

    schema = [
        """CREATE TABLE IF NOT EXISTS experiments (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             scenarioId INTEGER NOT NULL,
             name TEXT NOT NULL DEFAULT '',
             note TEXT NOT NULL DEFAULT '',
             arms TEXT NOT NULL DEFAULT '[]',
             repeats INTEGER NOT NULL DEFAULT 1,
             sheepModelId INTEGER,
             visitorModelId INTEGER,
             embedModelId INTEGER,
             status TEXT NOT NULL DEFAULT 'queued',
             createdAt REAL NOT NULL,
             finishedAt REAL
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("experiments", self.schema)

    def create(self, scenarioId, name, note, arms, repeats, sheepModelId, visitorModelId, embedModelId):
        cursor = self.database.write(
            "INSERT INTO experiments (scenarioId, name, note, arms, repeats, sheepModelId, visitorModelId, "
            "embedModelId, createdAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (scenarioId, name, note, json.dumps(arms, ensure_ascii=False), repeats, sheepModelId, visitorModelId,
             embedModelId, time.time()))
        return cursor.lastrowid

    def get(self, experimentId):
        row = self.database.readOne("SELECT * FROM experiments WHERE id = ?", (experimentId,))
        return self._experiment(row) if row else None

    def all(self):
        return [self._experiment(row) for row in self.database.read("SELECT * FROM experiments ORDER BY id DESC")]

    def setStatus(self, experimentId, status):
        finished = time.time() if status in ("done", "error", "stopped") else None
        self.database.write("UPDATE experiments SET status = ?, finishedAt = ? WHERE id = ?",
                            (status, finished, experimentId))

    def delete(self, experimentId):
        self.database.write("DELETE FROM experiments WHERE id = ?", (experimentId,))

    @staticmethod
    def _experiment(row):
        experiment = dict(row)
        experiment["arms"] = json.loads(experiment["arms"] or "[]")
        return experiment
