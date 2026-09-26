import json

from research.domains.scenarios.ScenarioOptions import ScenarioOptions


class serviceSaveScenario:
    """Creates or changes a scenario from the editor's form."""

    def __init__(self, scenarios):
        self.scenarios = scenarios

    def save(self, form, scenarioId=None):
        name = form.get("name", "").strip()
        if not name:
            raise ValueError("a scenario needs a name")
        options = ScenarioOptions({
            "quietThoughts": int(form.get("quietThoughts") or 0),
            "gapHours": float(form.get("gapHours") or 0),
            "consolidateAtNight": bool(form.get("consolidateAtNight")),
            "forgetAtNight": bool(form.get("forgetAtNight")),
            "parameters": json.loads(form.get("parameters") or "{}"),
        })
        seeds = json.loads(form.get("seeds") or "[]")
        if not isinstance(seeds, list):
            raise ValueError("seeds must be a JSON list")
        return self.scenarios.save({
            "name": name, "description": form.get("description", ""),
            "beingName": form.get("beingName", "").strip() or "Maya",
            "controlInstruction": form.get("controlInstruction", ""),
            "controlForm": "thread" if form.get("controlForm") == "thread" else "completion",
            "controlWindowTokens": int(form.get("controlWindowTokens") or 0),
            "options": options.toDict(), "seeds": seeds}, scenarioId)
