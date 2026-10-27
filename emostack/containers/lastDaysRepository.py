from emostack.containers.LastDays import LastDays


class lastDaysRepository:
    """The last days of a being in SQLite: one row per being, today, yesterday and the days before."""

    schema = [
        """CREATE TABLE IF NOT EXISTS lastDays (
             beingId INTEGER PRIMARY KEY,
             today TEXT NOT NULL DEFAULT '',
             yesterday TEXT NOT NULL DEFAULT '',
             before TEXT NOT NULL DEFAULT ''
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("lastDays", self.schema)

    def get(self, beingId):
        row = self.database.readOne("SELECT today, yesterday, before FROM lastDays WHERE beingId = ?", (beingId,))
        return LastDays(row["today"], row["yesterday"], row["before"]) if row else LastDays()

    def save(self, beingId, lastDays):
        self.database.write(
            "INSERT INTO lastDays (beingId, today, yesterday, before) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(beingId) DO UPDATE SET today = excluded.today, yesterday = excluded.yesterday, "
            "before = excluded.before",
            (beingId, lastDays.today, lastDays.yesterday, lastDays.before))

    def delete(self, beingId):
        self.database.write("DELETE FROM lastDays WHERE beingId = ?", (beingId,))
