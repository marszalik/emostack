class serviceTakeSnapshot:
    """A person's own copy of a being that has lived."""

    def __init__(self, engine, snapshots, most):
        self.engine = engine
        self.snapshots = snapshots
        self.most = most

    def take(self, person, slug):
        snapshot = self.snapshots.get(slug)
        if snapshot is None:
            raise ValueError("no such being to copy")
        if not person.isAdministrator() and len(self.engine.beings.all()) >= self.most:
            raise ValueError(f"at most {self.most} beings per person — delete one first")
        name = snapshot["name"]
        number = 2
        while self.engine.beings.named(name) is not None:
            name = f"{snapshot['name']} {number}"
            number += 1
        return self.engine.copyBeing(snapshot["path"], int(snapshot.get("beingId", 1)), name)
