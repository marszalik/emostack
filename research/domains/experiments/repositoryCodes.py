import time


class repositoryCodes:
    """The labels blind coders gave the runs of an experiment."""

    schema = [
        """CREATE TABLE IF NOT EXISTS codes (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             experimentId INTEGER NOT NULL,
             codingId INTEGER NOT NULL,
             coderModelId INTEGER NOT NULL,
             runId INTEGER NOT NULL,
             label TEXT,
             at REAL NOT NULL
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("codes", self.schema)

    def replace(self, experimentId, codingId, coderModelId, labels):
        """labels: {runId: label}. A new coding of the same act by the same coder replaces the old."""
        statements = [("DELETE FROM codes WHERE experimentId = ? AND codingId = ? AND coderModelId = ?",
                       (experimentId, codingId, coderModelId))]
        statements += [("INSERT INTO codes (experimentId, codingId, coderModelId, runId, label, at) VALUES (?, ?, ?, ?, ?, ?)",
                        (experimentId, codingId, coderModelId, runId, label, time.time())) for runId, label in labels.items()]
        self.database.writeMany(statements)

    def forExperiment(self, experimentId):
        return [dict(row) for row in self.database.read("SELECT * FROM codes WHERE experimentId = ?", (experimentId,))]
