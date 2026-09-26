class Cluster:
    """Records that are one recurring thought: rumination is one intrusive thought, not nine. The
    most intense member represents it."""

    def __init__(self, record):
        self.representative = record
        self.members = [record]

    def add(self, record):
        self.members.append(record)
        if record.intensity > self.representative.intensity:
            self.representative = record

    @property
    def count(self):
        return len(self.members)
