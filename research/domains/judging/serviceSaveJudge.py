class serviceSaveJudge:
    def __init__(self, judges):
        self.judges = judges

    def save(self, form, judgeId=None):
        return self.judges.save({
            "name": form.get("name", "").strip() or "judge",
            "modelId": int(form["modelId"]) if form.get("modelId") else None,
            "instruction": form.get("instruction", ""),
            "granularity": "session" if form.get("granularity") == "session" else "turn"}, judgeId)
