class serviceDeleteJudge:
    def __init__(self, judges):
        self.judges = judges

    def delete(self, judgeId):
        self.judges.delete(judgeId)
