class serviceDeleteScenario:
    def __init__(self, scenarios, roles, criteria, codings):
        self.scenarios = scenarios
        self.roles = roles
        self.criteria = criteria
        self.codings = codings

    def delete(self, scenarioId):
        self.roles.deleteForScenario(scenarioId)
        self.criteria.deleteForScenario(scenarioId)
        self.codings.deleteForScenario(scenarioId)
        self.scenarios.delete(scenarioId)
