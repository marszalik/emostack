class serviceDeleteCriterion:
    def __init__(self, criteria):
        self.criteria = criteria

    def delete(self, criterionId):
        self.criteria.delete(criterionId)
