class Association:
    """A memory the present brought to mind: involuntarily, by what was just said, or deliberately,
    by a search the being made."""

    INVOLUNTARY = "involuntary"
    DELIBERATE = "deliberate"

    def __init__(self, record, origin):
        self.record = record
        self.origin = origin
