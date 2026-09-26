class repositoryPeople:
    """People with a role: 1 guest, 2 friend, 3 administrator. Administrators named in the settings
    are always administrators and are not stored here."""

    schema = ["CREATE TABLE IF NOT EXISTS people (email TEXT PRIMARY KEY, level INTEGER NOT NULL)"]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("people", self.schema)

    def all(self):
        return [dict(row) for row in self.database.read("SELECT * FROM people ORDER BY level DESC, email")]

    def level(self, email):
        row = self.database.readOne("SELECT level FROM people WHERE email = ?", (email,))
        return row["level"] if row else None

    def save(self, email, level):
        self.database.write("INSERT INTO people (email, level) VALUES (?, ?) "
                            "ON CONFLICT(email) DO UPDATE SET level = excluded.level", (email, level))

    def delete(self, email):
        self.database.write("DELETE FROM people WHERE email = ?", (email,))
