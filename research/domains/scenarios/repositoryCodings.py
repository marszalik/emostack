import json


class repositoryCodings:
    """Blind codings of a scenario, written before the runs: which day's replies a coder reads, the
    criterion, the labels it may give, and whether it reads all the being's replies of that day or
    only the last."""

    schema = [
        """CREATE TABLE IF NOT EXISTS codings (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             scenarioId INTEGER NOT NULL,
             name TEXT NOT NULL,
             criterion TEXT NOT NULL,
             labels TEXT NOT NULL DEFAULT '[]',
             dayIndex INTEGER NOT NULL DEFAULT 0,
             which TEXT NOT NULL DEFAULT 'all',
             position INTEGER NOT NULL DEFAULT 0
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("codings", self.schema)

    def forScenario(self, scenarioId):
        return [self._coding(row) for row in self.database.read(
            "SELECT * FROM codings WHERE scenarioId = ? ORDER BY position, id", (scenarioId,))]

    def get(self, codingId):
        row = self.database.readOne("SELECT * FROM codings WHERE id = ?", (codingId,))
        return self._coding(row) if row else None

    def save(self, scenarioId, values, codingId=None):
        labels = json.dumps(values["labels"], ensure_ascii=False)
        if codingId:
            self.database.write("UPDATE codings SET name = ?, criterion = ?, labels = ?, dayIndex = ?, which = ? WHERE id = ?",
                                (values["name"], values["criterion"], labels, values["dayIndex"], values["which"], codingId))
            return codingId
        cursor = self.database.write(
            "INSERT INTO codings (scenarioId, name, criterion, labels, dayIndex, which, position) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (scenarioId, values["name"], values["criterion"], labels, values["dayIndex"], values["which"],
             len(self.forScenario(scenarioId))))
        return cursor.lastrowid

    def delete(self, codingId):
        self.database.write("DELETE FROM codings WHERE id = ?", (codingId,))

    def deleteForScenario(self, scenarioId):
        self.database.write("DELETE FROM codings WHERE scenarioId = ?", (scenarioId,))

    @staticmethod
    def _coding(row):
        coding = dict(row)
        coding["labels"] = json.loads(coding["labels"] or "[]")
        return coding
