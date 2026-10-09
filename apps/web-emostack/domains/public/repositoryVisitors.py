import time


class repositoryVisitors:
    """What the room keeps about its visitors, in the application's own database: the visits of the
    day (so that one person does not hold the being all day), the letters left while it slept and
    the answers they got, and the reports."""

    schema = [
        """CREATE TABLE IF NOT EXISTS publicVisits (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             visitor TEXT NOT NULL,
             address TEXT NOT NULL,
             name TEXT NOT NULL,
             day TEXT NOT NULL,
             at REAL NOT NULL
           )""",
        "CREATE INDEX IF NOT EXISTS publicVisitsDay ON publicVisits(day, visitor)",
        """CREATE TABLE IF NOT EXISTS publicMail (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             visitor TEXT NOT NULL,
             address TEXT NOT NULL,
             name TEXT NOT NULL,
             words TEXT NOT NULL,
             night TEXT NOT NULL,
             at REAL NOT NULL,
             reply TEXT,
             deliveredAt REAL
           )""",
        """CREATE TABLE IF NOT EXISTS publicReports (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             visitor TEXT NOT NULL,
             address TEXT NOT NULL,
             about TEXT NOT NULL,
             note TEXT NOT NULL DEFAULT '',
             at REAL NOT NULL
           )""",
    ]

    def __init__(self, database):
        self.database = database
        database.ensureSchema("publicVisitors", self.schema)

    def visitsToday(self, visitor, address, day):
        byVisitor = self.database.readOne("SELECT COUNT(*) AS n FROM publicVisits WHERE day = ? AND visitor = ?",
                                          (day, visitor))["n"]
        byAddress = self.database.readOne("SELECT COUNT(*) AS n FROM publicVisits WHERE day = ? AND address = ?",
                                          (day, address))["n"]
        return max(byVisitor, byAddress)

    def visited(self, visitor, address, name, day):
        self.database.write("INSERT INTO publicVisits (visitor, address, name, day, at) VALUES (?, ?, ?, ?, ?)",
                            (visitor, address, name, day, time.time()))

    def mailTonight(self, visitor, address, night):
        byVisitor = self.database.readOne("SELECT COUNT(*) AS n FROM publicMail WHERE night = ? AND visitor = ?",
                                          (night, visitor))["n"]
        byAddress = self.database.readOne("SELECT COUNT(*) AS n FROM publicMail WHERE night = ? AND address = ?",
                                          (night, address))["n"]
        return max(byVisitor, byAddress)

    def leaveMail(self, visitor, address, name, words, night):
        self.database.write(
            "INSERT INTO publicMail (visitor, address, name, words, night, at) VALUES (?, ?, ?, ?, ?, ?)",
            (visitor, address, name, words, night, time.time()))

    def undelivered(self):
        return [dict(row) for row in self.database.read(
            "SELECT * FROM publicMail WHERE deliveredAt IS NULL ORDER BY id LIMIT 20")]

    def deliver(self, mailId, reply):
        self.database.write("UPDATE publicMail SET reply = ?, deliveredAt = ? WHERE id = ?", (reply, time.time(), mailId))

    def mailOf(self, visitor):
        return [dict(row) for row in self.database.read(
            "SELECT name, words, at, reply, deliveredAt FROM publicMail WHERE visitor = ? ORDER BY id DESC LIMIT 3",
            (visitor,))]

    def report(self, visitor, address, about, note):
        self.database.write("INSERT INTO publicReports (visitor, address, about, note, at) VALUES (?, ?, ?, ?, ?)",
                            (visitor, address, about[:2000], note[:500], time.time()))

    def reports(self, limit=50):
        return [dict(row) for row in self.database.read("SELECT * FROM publicReports ORDER BY id DESC LIMIT ?", (limit,))]
