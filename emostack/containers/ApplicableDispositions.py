class ApplicableDispositions:
    """The learned dispositions that fit what is happening now: zero to three. In view only while
    the reply is composed."""

    def __init__(self, dispositions=None):
        self.dispositions = list(dispositions or [])

    def rules(self):
        return [disposition.rule for disposition in self.dispositions]

    def __len__(self):
        return len(self.dispositions)
