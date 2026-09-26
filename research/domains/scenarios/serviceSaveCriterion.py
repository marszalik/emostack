class serviceSaveCriterion:
    def __init__(self, criteria):
        self.criteria = criteria

    def save(self, scenarioId, form, criterionId=None):
        name = form.get("name", "").strip()
        if not name:
            raise ValueError("a criterion needs a name")
        return self.criteria.save(scenarioId, name, form.get("description", ""), criterionId)
