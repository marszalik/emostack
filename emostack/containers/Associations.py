from emostack.containers.Association import Association


class Associations:
    """What the trigger brought to mind, and what the being searched for. The strongest pass into
    the state; the rest stay in view in the focus."""

    def __init__(self):
        self.items = []

    def add(self, records, origin=Association.INVOLUNTARY):
        known = self.ids()
        for record in records:
            if record.id not in known:
                self.items.append(Association(record, origin))
                known.add(record.id)

    def records(self):
        return [item.record for item in self.items]

    def ids(self):
        return {item.record.id for item in self.items}

    def __len__(self):
        return len(self.items)
