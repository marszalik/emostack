class JudgedSeries:
    """One run as a judge sees it: a letter instead of its arm, and its turns."""

    def __init__(self, letter, runId, turns):
        self.letter = letter
        self.runId = runId
        self.turns = [turn for turn in turns if turn["speaker"] in ("sheep", "visitor")]

    def beingTurns(self):
        return [turn for turn in self.turns if turn["speaker"] == "sheep"]

    def beingTurnIndexes(self):
        return [turn["turnIndex"] for turn in self.beingTurns()]

    def days(self):
        seen = []
        for turn in self.beingTurns():
            if all(day != turn["dayIndex"] for day, _ in seen):
                seen.append((turn["dayIndex"], turn["person"]))
        return seen
