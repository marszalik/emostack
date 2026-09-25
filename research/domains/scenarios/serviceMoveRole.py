class serviceMoveRole:
    """Moves a visitor one day earlier or later."""

    def __init__(self, roles):
        self.roles = roles

    def move(self, scenarioId, roleId, step):
        ids = [role["id"] for role in self.roles.forScenario(scenarioId)]
        index = ids.index(roleId)
        target = max(0, min(len(ids) - 1, index + step))
        ids.insert(target, ids.pop(index))
        self.roles.reorder(scenarioId, ids)
