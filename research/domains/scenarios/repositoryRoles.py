class repositoryRoles:
    """The visitors of a scenario, in the order of the days: one role is one conversation."""

    schema = [
        """CREATE TABLE IF NOT EXISTS roles (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             scenarioId INTEGER NOT NULL,
             name TEXT NOT NULL,
             description TEXT NOT NULL DEFAULT '',
             instruction TEXT NOT NULL DEFAULT '',
             windowFrom INTEGER NOT NULL DEFAULT 3,
             windowTo INTEGER NOT NULL DEFAULT 6,
             gapHours REAL,
             position INTEGER NOT NULL DEFAULT 0
           )""",
    ]
    fields = ("name", "description", "instruction", "windowFrom", "windowTo", "gapHours")

    def __init__(self, database):
        self.database = database
        database.ensureSchema("roles", self.schema)

    def forScenario(self, scenarioId):
        return [dict(row) for row in self.database.read(
            "SELECT * FROM roles WHERE scenarioId = ? ORDER BY position, id", (scenarioId,))]

    def get(self, roleId):
        row = self.database.readOne("SELECT * FROM roles WHERE id = ?", (roleId,))
        return dict(row) if row else None

    def save(self, scenarioId, values, roleId=None):
        names = [name for name in self.fields if name in values]
        if roleId:
            self.database.write(f"UPDATE roles SET {', '.join(f'{name} = ?' for name in names)} WHERE id = ?",
                                [values[name] for name in names] + [roleId])
            return roleId
        position = len(self.forScenario(scenarioId))
        cursor = self.database.write(
            f"INSERT INTO roles (scenarioId, position, {', '.join(names)}) "
            f"VALUES (?, ?, {', '.join('?' for _ in names)})", [scenarioId, position] + [values[name] for name in names])
        return cursor.lastrowid

    def delete(self, roleId):
        self.database.write("DELETE FROM roles WHERE id = ?", (roleId,))

    def reorder(self, scenarioId, roleIds):
        self.database.writeMany([("UPDATE roles SET position = ? WHERE id = ? AND scenarioId = ?",
                                  (position, roleId, scenarioId)) for position, roleId in enumerate(roleIds)])

    def deleteForScenario(self, scenarioId):
        self.database.write("DELETE FROM roles WHERE scenarioId = ?", (scenarioId,))
