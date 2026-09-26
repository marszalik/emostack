class accessibilitySlotRepository:
    """Which constructs a being holds in its accessibility slot, and when each was last brought to
    mind."""

    schema = [
        """CREATE TABLE IF NOT EXISTS slot (
             beingId INTEGER NOT NULL,
             recordId TEXT NOT NULL,
             activatedAt REAL NOT NULL,
             PRIMARY KEY (beingId, recordId)
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("slot", self.schema)

    def held(self, beingId):
        rows = self.database.read(
            "SELECT recordId, activatedAt FROM slot WHERE beingId = ? ORDER BY activatedAt", (beingId,))
        return [(row["recordId"], float(row["activatedAt"])) for row in rows]

    def replace(self, beingId, places):
        statements = [("DELETE FROM slot WHERE beingId = ?", (beingId,))]
        statements += [("INSERT INTO slot (beingId, recordId, activatedAt) VALUES (?, ?, ?)",
                        (beingId, recordId, float(at))) for recordId, at in places]
        self.database.writeMany(statements)
