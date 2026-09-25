class serviceExportScenario:
    """A scenario as a JSON document that can be kept in the repository and imported elsewhere."""

    def __init__(self, scenarios, roles, criteria, codings):
        self.scenarios = scenarios
        self.roles = roles
        self.criteria = criteria
        self.codings = codings

    def export(self, scenarioId):
        scenario = self.scenarios.get(scenarioId)
        if scenario is None:
            raise ValueError(f"no scenario {scenarioId}")
        return {
            "name": scenario["name"], "description": scenario["description"], "beingName": scenario["beingName"],
            "controlInstruction": scenario["controlInstruction"], "controlForm": scenario["controlForm"],
            "controlWindowTokens": scenario["controlWindowTokens"], "options": scenario["options"],
            "seeds": scenario["seeds"],
            "roles": [{key: role[key] for key in ("name", "description", "instruction", "windowFrom", "windowTo",
                                                   "gapHours")} for role in self.roles.forScenario(scenarioId)],
            "criteria": [{"name": criterion["name"], "description": criterion["description"]}
                         for criterion in self.criteria.forScenario(scenarioId)],
            "codings": [{key: coding[key] for key in ("name", "criterion", "labels", "dayIndex", "which")}
                        for coding in self.codings.forScenario(scenarioId)],
        }
