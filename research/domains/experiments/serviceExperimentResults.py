import statistics

from research.domains.experiments.serviceCompareArms import serviceCompareArms


class serviceExperimentResults:
    """Per judge and criterion: each run's mean score, and the arms compared pair by pair."""

    def __init__(self, runs, scores, judges, criteria):
        self.runs = runs
        self.scores = scores
        self.judges = judges
        self.criteria = criteria

    def results(self, experiment):
        collected = {}
        for run in self.runs.forExperiment(experiment["id"]):
            for score in self.scores.forRun(run["id"]):
                if score["score"] is None:
                    continue
                collected.setdefault((score["judgeId"], score["criterionId"]), {}) \
                         .setdefault(run["armLabel"], {}).setdefault(run["iteration"], []).append(score["score"])
        names = {criterion["id"]: criterion["name"] for criterion in self.criteria.forScenario(experiment["scenarioId"])}
        judgeNames = {judge["id"]: judge["name"] for judge in self.judges.all()}
        out = []
        for (judgeId, criterionId), arms in sorted(collected.items()):
            perArm = {arm: {repeat: statistics.mean(values) for repeat, values in repeats.items()}
                      for arm, repeats in arms.items()}
            out.append({"judge": judgeNames.get(judgeId, judgeId), "criterion": names.get(criterionId, criterionId),
                        "perArm": {arm: [round(perArm[arm][r], 2) for r in sorted(perArm[arm])] for arm in perArm},
                        "comparisons": serviceCompareArms().compare(perArm) if len(perArm) > 1 else []})
        return out
