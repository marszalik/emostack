class CallLog:
    """The calls of one LLM model since they were last taken: attached to the turn they belong to,
    so that every turn of a run can be audited with the prompts behind it."""

    def __init__(self, processor):
        self.calls = []
        processor.addRecorder(self.calls.append)

    def take(self):
        calls, self.calls[:] = list(self.calls), []
        return calls
