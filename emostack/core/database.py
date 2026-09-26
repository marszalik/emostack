import os
import sqlite3
import threading


class database:
    """One SQLite file. Repositories declare their own tables; this class only holds the
    connection, serialises writes and applies a repository's schema once."""

    def __init__(self, path):
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        self.path = path
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self._applied = set()

    def ensureSchema(self, owner, statements):
        if owner in self._applied:
            return
        with self.lock:
            for statement in statements:
                self.connection.execute(statement)
            self.connection.commit()
        self._applied.add(owner)

    def read(self, sql, parameters=()):
        return self.connection.execute(sql, parameters).fetchall()

    def readOne(self, sql, parameters=()):
        return self.connection.execute(sql, parameters).fetchone()

    def write(self, sql, parameters=()):
        with self.lock:
            cursor = self.connection.execute(sql, parameters)
            self.connection.commit()
            return cursor

    def writeMany(self, statements):
        """Several writes in one transaction: [(sql, parameters), ...]."""
        with self.lock:
            for sql, parameters in statements:
                self.connection.execute(sql, parameters)
            self.connection.commit()

    def close(self):
        self.connection.close()
