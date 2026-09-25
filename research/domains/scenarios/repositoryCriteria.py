class repositoryCriteria:
    """What judges score in a scenario: one criterion is one behaviour with its scoring rules."""

    schema = [
        """CREATE TABLE IF NOT EXISTS criteria (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             scenarioId INTEGER NOT NULL,
             name TEXT NOT NULL,
             description TEXT NOT NULL DEFAULT '',
             position INTEGER NOT NULL DEFAULT 0
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("criteria", self.schema)

    def forScenario(self, scenarioId):
        return [dict(row) for row in self.database.read(
            "SELECT * FROM criteria WHERE scenarioId = ? ORDER BY position, id", (scenarioId,))]

    def save(self, scenarioId, name, description, criterionId=None):
        if criterionId:
            self.database.write("UPDATE criteria SET name = ?, description = ? WHERE id = ?",
                                (name, description, criterionId))
            return criterionId
        position = len(self.forScenario(scenarioId))
        cursor = self.database.write(
            "INSERT INTO criteria (scenarioId, name, description, position) VALUES (?, ?, ?, ?)",
            (scenarioId, name, description, position))
        return cursor.lastrowid

    def delete(self, criterionId):
        self.database.write("DELETE FROM criteria WHERE id = ?", (criterionId,))

    def deleteForScenario(self, scenarioId):
        self.database.write("DELETE FROM criteria WHERE scenarioId = ?", (scenarioId,))
