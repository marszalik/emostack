class ScenarioOptions:
    """How a scenario's life runs: how many thoughts the being has in the quiet after each
    conversation, how many hours pass between conversations, whether the night between them folds
    the day and forgets, and which engine parameters differ from the defaults (an ablation sets,
    for example, slotSize to 0)."""

    defaults = {"quietThoughts": 1, "gapHours": 24.0, "consolidateAtNight": False, "forgetAtNight": True,
                "parameters": {}}

    def __init__(self, values=None):
        merged = dict(self.defaults)
        merged.update(values or {})
        self.quietThoughts = int(merged["quietThoughts"])
        self.gapHours = float(merged["gapHours"])
        self.consolidateAtNight = bool(merged["consolidateAtNight"])
        self.forgetAtNight = bool(merged["forgetAtNight"])
        self.parameters = dict(merged["parameters"] or {})

    def toDict(self):
        return {"quietThoughts": self.quietThoughts, "gapHours": self.gapHours,
                "consolidateAtNight": self.consolidateAtNight, "forgetAtNight": self.forgetAtNight,
                "parameters": self.parameters}
