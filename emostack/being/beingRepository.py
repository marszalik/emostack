from emostack.being.Being import Being
from emostack.being.Temperament import Temperament
from emostack.being.Wakefulness import Wakefulness


class beingRepository:
    """Beings in SQLite."""

    schema = [
        """CREATE TABLE IF NOT EXISTS beings (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT UNIQUE NOT NULL,
             createdAt REAL NOT NULL,
             valenceBias REAL NOT NULL DEFAULT 0,
             intensityAmplification REAL NOT NULL DEFAULT 1,
             avoidanceWeight REAL NOT NULL DEFAULT 2,
             wakefulness TEXT NOT NULL DEFAULT 'asleep',
             lastActivity REAL NOT NULL DEFAULT 0,
             introspectedIdle INTEGER NOT NULL DEFAULT 0,
             wakePending INTEGER NOT NULL DEFAULT 0,
             wokeAt REAL NOT NULL DEFAULT 0,
             sleptAt REAL NOT NULL DEFAULT 0,
             consolidated INTEGER NOT NULL DEFAULT 1
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("beings", self.schema)

    def create(self, name, temperament, now):
        cursor = self.database.write(
            "INSERT INTO beings (name, createdAt, valenceBias, intensityAmplification, avoidanceWeight) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, now, temperament.valenceBias, temperament.intensityAmplification,
             temperament.avoidanceWeight))
        return self.get(cursor.lastrowid)

    def get(self, beingId):
        row = self.database.readOne("SELECT * FROM beings WHERE id = ?", (beingId,))
        return self._being(row) if row else None

    def named(self, name):
        row = self.database.readOne("SELECT * FROM beings WHERE name = ?", (name,))
        return self._being(row) if row else None

    def all(self):
        return [self._being(row) for row in self.database.read("SELECT * FROM beings ORDER BY id")]

    def delete(self, beingId):
        self.database.write("DELETE FROM beings WHERE id = ?", (beingId,))

    def saveWakefulness(self, being):
        self.database.write(
            "UPDATE beings SET wakefulness = ?, lastActivity = ?, introspectedIdle = ?, wakePending = ?, "
            "wokeAt = ?, sleptAt = ?, consolidated = ? WHERE id = ?",
            (being.wakefulness.value, being.lastActivity, int(being.introspectedIdle),
             int(being.wakePending), being.wokeAt, being.sleptAt, int(being.consolidated), being.id))

    @staticmethod
    def _being(row):
        return Being(
            id=row["id"], name=row["name"],
            temperament=Temperament(row["valenceBias"], row["intensityAmplification"], row["avoidanceWeight"]),
            createdAt=row["createdAt"], wakefulness=Wakefulness(row["wakefulness"]),
            lastActivity=row["lastActivity"], introspectedIdle=bool(row["introspectedIdle"]),
            wakePending=bool(row["wakePending"]), wokeAt=row["wokeAt"], sleptAt=row["sleptAt"],
            consolidated=bool(row["consolidated"]))
