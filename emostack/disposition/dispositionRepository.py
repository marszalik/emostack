from emostack.disposition.Disposition import Disposition


class dispositionRepository:
    """Learned dispositions in SQLite."""

    schema = [
        """CREATE TABLE IF NOT EXISTS dispositions (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             beingId INTEGER NOT NULL,
             rule TEXT NOT NULL,
             weight REAL NOT NULL,
             count INTEGER NOT NULL DEFAULT 1,
             updatedAt REAL NOT NULL DEFAULT 0
           )""",
        "CREATE INDEX IF NOT EXISTS dispositionsOfBeing ON dispositions(beingId)",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("dispositions", self.schema)

    def strongestFirst(self, beingId, limit):
        rows = self.database.read(
            "SELECT * FROM dispositions WHERE beingId = ? ORDER BY ABS(weight) DESC LIMIT ?",
            (beingId, limit))
        return [self._disposition(row) for row in rows]

    def any(self, beingId):
        return self.database.readOne("SELECT 1 FROM dispositions WHERE beingId = ? LIMIT 1",
                                     (beingId,)) is not None

    def add(self, beingId, rule, weight, now):
        self.database.write(
            "INSERT INTO dispositions (beingId, rule, weight, count, updatedAt) VALUES (?, ?, ?, 1, ?)",
            (beingId, rule, float(weight), now))

    def rewrite(self, disposition, rule, weight, count, now):
        self.database.write(
            "UPDATE dispositions SET rule = ?, weight = ?, count = ?, updatedAt = ? WHERE id = ?",
            (rule, float(weight), int(count), now, disposition.id))

    def recount(self, disposition, count, now):
        self.database.write("UPDATE dispositions SET count = ?, updatedAt = ? WHERE id = ?",
                            (int(count), now, disposition.id))

    def weaken(self, disposition, amount, now):
        """Moves the weight toward zero by `amount`, never across it."""
        self.database.write(
            "UPDATE dispositions SET weight = CASE WHEN weight > 0 THEN MAX(0, weight - ?) "
            "ELSE MIN(0, weight + ?) END, updatedAt = ? WHERE id = ?",
            (float(amount), float(amount), now, disposition.id))

    def deleteBeing(self, beingId):
        self.database.write("DELETE FROM dispositions WHERE beingId = ?", (beingId,))

    @staticmethod
    def _disposition(row):
        return Disposition(row["id"], row["beingId"], row["rule"], row["weight"], row["count"],
                           row["updatedAt"])
