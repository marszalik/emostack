import hashlib
import json
import os


class serviceStoreFor:
    """Where a person's beings live: every person has a store of their own, so that nothing they do
    touches anyone else's beings and every cost goes on their own key. Administrators share the
    server's store."""

    def __init__(self, application):
        self.folder = application.config.dataFolder

    def path(self, person):
        if person.isAdministrator():
            folder = os.path.join(self.folder, "shared")
        else:
            folder = os.path.join(self.folder, "people", hashlib.sha1(person.email.encode()).hexdigest()[:16])
        if not os.path.isdir(folder):
            os.makedirs(folder, mode=0o700)
            with open(os.path.join(folder, "owner.json"), "w", encoding="utf-8") as f:
                json.dump({"email": person.email}, f)
        return os.path.join(folder, "emostack.db")

    def owners(self):
        """[(email or None for the shared store, store path)] for the clock."""
        found = []
        shared = os.path.join(self.folder, "shared", "emostack.db")
        if os.path.exists(shared):
            found.append((None, shared))
        people = os.path.join(self.folder, "people")
        for name in sorted(os.listdir(people)) if os.path.isdir(people) else []:
            store = os.path.join(people, name, "emostack.db")
            owner = os.path.join(people, name, "owner.json")
            if os.path.exists(store) and os.path.exists(owner):
                with open(owner, encoding="utf-8") as f:
                    found.append((json.load(f)["email"], store))
        return found
