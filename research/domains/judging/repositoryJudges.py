class repositoryJudges:
    """Judges: an LLM model, the researcher's scoring instruction, and whether it scores each turn
    of the being or each whole conversation."""

    schema = [
        """CREATE TABLE IF NOT EXISTS judges (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             modelId INTEGER,
             instruction TEXT NOT NULL DEFAULT '',
             granularity TEXT NOT NULL DEFAULT 'turn'
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("judges", self.schema)

    def all(self):
        return [dict(row) for row in self.database.read("SELECT * FROM judges ORDER BY name")]

    def get(self, judgeId):
        row = self.database.readOne("SELECT * FROM judges WHERE id = ?", (judgeId,))
        return dict(row) if row else None

    def save(self, values, judgeId=None):
        if judgeId:
            self.database.write("UPDATE judges SET name = ?, modelId = ?, instruction = ?, granularity = ? WHERE id = ?",
                                (values["name"], values["modelId"], values["instruction"], values["granularity"], judgeId))
            return judgeId
        cursor = self.database.write("INSERT INTO judges (name, modelId, instruction, granularity) VALUES (?, ?, ?, ?)",
                                     (values["name"], values["modelId"], values["instruction"], values["granularity"]))
        return cursor.lastrowid

    def delete(self, judgeId):
        self.database.write("DELETE FROM judges WHERE id = ?", (judgeId,))
