from research.domains.scenarios.ScenarioOptions import ScenarioOptions


class serviceImportScenario:
    """Creates a scenario from its JSON document."""

    def __init__(self, scenarios, roles, criteria, codings):
        self.scenarios = scenarios
        self.roles = roles
        self.criteria = criteria
        self.codings = codings

    def load(self, document):
        scenarioId = self.scenarios.save({
            "name": document["name"], "description": document.get("description", ""),
            "beingName": document.get("beingName", "Maya"),
            "controlInstruction": document.get("controlInstruction", ""),
            "controlForm": document.get("controlForm", "completion"),
            "controlWindowTokens": int(document.get("controlWindowTokens", 0)),
            "options": ScenarioOptions(document.get("options")).toDict(),
            "seeds": document.get("seeds", [])})
        for role in document.get("roles", []):
            windowFrom = int(role.get("windowFrom") or 3)
            self.roles.save(scenarioId, {
                "name": role["name"], "description": role.get("description") or "",
                "instruction": role.get("instruction") or "", "windowFrom": windowFrom,
                "windowTo": max(windowFrom, int(role.get("windowTo") or windowFrom)),
                "gapHours": role.get("gapHours")})
        for criterion in document.get("criteria", []):
            self.criteria.save(scenarioId, criterion["name"], criterion.get("description", ""))
        for coding in document.get("codings", []):
            self.codings.save(scenarioId, {"name": coding["name"], "criterion": coding["criterion"],
                                           "labels": coding["labels"], "dayIndex": int(coding.get("dayIndex", 0)),
                                           "which": coding.get("which", "all")})
        return scenarioId
