import json
import time


class repositoryScenarios:
    """Scenarios: who the being is called, what it carries at birth, how the days pass, and the
    instruction of the control arm."""

    schema = [
        """CREATE TABLE IF NOT EXISTS scenarios (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             description TEXT NOT NULL DEFAULT '',
             beingName TEXT NOT NULL DEFAULT 'Maya',
             controlInstruction TEXT NOT NULL DEFAULT '',
             controlForm TEXT NOT NULL DEFAULT 'completion',
             controlWindowTokens INTEGER NOT NULL DEFAULT 0,
             options TEXT NOT NULL DEFAULT '{}',
             seeds TEXT NOT NULL DEFAULT '[]',
             createdAt REAL NOT NULL,
             updatedAt REAL NOT NULL
           )""",
    ]
    fields = ("name", "description", "beingName", "controlInstruction", "controlForm", "controlWindowTokens",
              "options", "seeds")

    def __init__(self, database):
        self.database = database
        database.ensureSchema("scenarios", self.schema)

    def all(self):
        return [self._scenario(row) for row in self.database.read("SELECT * FROM scenarios ORDER BY name")]

    def get(self, scenarioId):
        row = self.database.readOne("SELECT * FROM scenarios WHERE id = ?", (scenarioId,))
        return self._scenario(row) if row else None

    def save(self, values, scenarioId=None):
        values = dict(values)
        for name in ("options", "seeds"):
            if name in values and not isinstance(values[name], str):
                values[name] = json.dumps(values[name], ensure_ascii=False)
        names = [name for name in self.fields if name in values]
        now = time.time()
        if scenarioId:
            self.database.write(
                f"UPDATE scenarios SET {', '.join(f'{name} = ?' for name in names)}, updatedAt = ? WHERE id = ?",
                [values[name] for name in names] + [now, scenarioId])
            return scenarioId
        cursor = self.database.write(
            f"INSERT INTO scenarios ({', '.join(names)}, createdAt, updatedAt) "
            f"VALUES ({', '.join('?' for _ in names)}, ?, ?)", [values[name] for name in names] + [now, now])
        return cursor.lastrowid

    def delete(self, scenarioId):
        self.database.write("DELETE FROM scenarios WHERE id = ?", (scenarioId,))

    @staticmethod
    def _scenario(row):
        scenario = dict(row)
        scenario["options"] = json.loads(scenario["options"] or "{}")
        scenario["seeds"] = json.loads(scenario["seeds"] or "[]")
        return scenario
