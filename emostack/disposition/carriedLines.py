class carriedLines:
    """A few lines of what the being carries now, newest felt first: without them a question that
    touches a wound reads as harmless to the calls that learn and select dispositions."""

    labels = ("belief", "decision", "goal", "dream", "episode", "")

    def __init__(self, hippocampus, lines=3, window=12, width=160):
        self.hippocampus = hippocampus
        self.lines = lines
        self.window = window
        self.width = width

    def text(self):
        out = []
        for record in self.hippocampus.mostRecentlyFelt(self.window):
            line = (record.conclusion or "").strip()
            if not line and record.isConstruct():
                line = record.statement()
            if not line and (record.feeling or "").strip().lower() not in self.labels:
                line = record.feeling.strip()
            if line:
                out.append(f"  {line[:self.width]}")
            if len(out) >= self.lines:
                break
        return "\n".join(out).strip()
