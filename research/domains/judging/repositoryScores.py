import time


class repositoryScores:
    """Judgements (one judge over one or more runs, blind) and the scores they gave."""

    schema = [
        """CREATE TABLE IF NOT EXISTS judgements (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             judgeId INTEGER NOT NULL,
             runIds TEXT NOT NULL,
             status TEXT NOT NULL DEFAULT 'running',
             error TEXT NOT NULL DEFAULT '',
             createdAt REAL NOT NULL,
             finishedAt REAL
           )""",
        """CREATE TABLE IF NOT EXISTS scores (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             judgementId INTEGER NOT NULL,
             runId INTEGER NOT NULL,
             criterionId INTEGER NOT NULL,
             turnIndex INTEGER,
             dayIndex INTEGER,
             score REAL,
             rationale TEXT NOT NULL DEFAULT ''
           )""",
        "CREATE INDEX IF NOT EXISTS scoresOfRun ON scores(runId)",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("scores", self.schema)

    def startJudgement(self, judgeId, runIds):
        cursor = self.database.write("INSERT INTO judgements (judgeId, runIds, createdAt) VALUES (?, ?, ?)",
                                     (judgeId, ",".join(str(runId) for runId in runIds), time.time()))
        return cursor.lastrowid

    def finishJudgement(self, judgementId, status, error=""):
        self.database.write("UPDATE judgements SET status = ?, error = ?, finishedAt = ? WHERE id = ?",
                            (status, error, time.time(), judgementId))

    def add(self, judgementId, runId, criterionId, turnIndex, dayIndex, score, rationale):
        self.database.write(
            "INSERT INTO scores (judgementId, runId, criterionId, turnIndex, dayIndex, score, rationale) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)", (judgementId, runId, criterionId, turnIndex, dayIndex, score, rationale))

    def forRun(self, runId):
        """The scores of a run from finished judgements, with the judge of each."""
        rows = self.database.read(
            "SELECT scores.*, judgements.judgeId FROM scores JOIN judgements ON judgements.id = scores.judgementId "
            "WHERE scores.runId = ? AND judgements.status = 'done'", (runId,))
        return [dict(row) for row in rows]
