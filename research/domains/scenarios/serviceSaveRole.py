class serviceSaveRole:
    """A visitor of the scenario. The instruction goes to the visitor's LLM model. It may start
    with [VERBATIM] (the lines, word for word, one per line) or [ANCHORS] (each line must end with
    the anchor sentence; the model may put one short reaction before it)."""

    def __init__(self, roles):
        self.roles = roles

    def save(self, scenarioId, form, roleId=None):
        gap = (form.get("gapHours") or "").strip()
        windowFrom = max(1, int(form.get("windowFrom") or 1))
        return self.roles.save(scenarioId, {
            "name": form.get("name", "").strip() or "Visitor",
            "description": form.get("description", ""),
            "instruction": form.get("instruction", ""),
            "windowFrom": windowFrom,
            "windowTo": max(windowFrom, int(form.get("windowTo") or windowFrom)),
            "gapHours": float(gap) if gap else None}, roleId)
