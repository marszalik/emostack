import os
import sqlite3

from domains.beings.serviceStoreFor import serviceStoreFor
from domains.models.repositoryPersonalModels import repositoryPersonalModels


class serviceEveryone:
    """Everyone who has signed in at least once: a person's store is made on their first visit.
    For each: when they first came, when their store last changed, how many beings they have, and
    whether they brought a model of their own."""

    def __init__(self, application, whoIsThis):
        self.stores = serviceStoreFor(application)
        self.models = repositoryPersonalModels(application.database)
        self.whoIsThis = whoIsThis

    def list(self):
        people = []
        for email, store in self.stores.owners():
            if email is None:
                continue
            folder = os.path.dirname(store)
            people.append({
                "email": email,
                "level": self.whoIsThis.levelOf(email),
                "firstVisit": os.path.getmtime(os.path.join(folder, "owner.json")),
                "lastActivity": max(os.path.getmtime(os.path.join(folder, name)) for name in os.listdir(folder)),
                "beings": self._beings(store),
                "ownModel": self.models.get(email) is not None,
            })
        return sorted(people, key=lambda person: person["lastActivity"], reverse=True)

    @staticmethod
    def _beings(store):
        connection = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
        try:
            return connection.execute("SELECT COUNT(*) FROM beings").fetchone()[0]
        except sqlite3.OperationalError:
            return 0
        finally:
            connection.close()
