class serviceSaveCoding:
    def __init__(self, codings):
        self.codings = codings

    def save(self, scenarioId, form, codingId=None):
        labels = [label.strip() for label in form.get("labels", "").split(",") if label.strip()]
        if not form.get("name", "").strip() or not form.get("criterion", "").strip() or len(labels) < 2:
            raise ValueError("a coding needs a name, a criterion and at least two labels")
        return self.codings.save(scenarioId, {
            "name": form["name"].strip(), "criterion": form["criterion"].strip(), "labels": labels,
            "dayIndex": max(0, int(form.get("day") or 1) - 1),
            "which": "last" if form.get("which") == "last" else "all"}, codingId)
