import json

from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.lives.serviceStartRun import serviceStartRun


class serviceCreateExperiment:
    """An experiment from the form: arm A is the being as configured, arm B the being with
    parameters changed (an ablation), arm C the control; every run is queued at once."""

    def __init__(self, application):
        self.application = application
        self.experiments = repositoryExperiments(application.database)
        self.starter = serviceStartRun(application)

    def create(self, form):
        arms = []
        if form.get("armA"):
            arms.append({"label": "A", "arm": "sheep", "parameters": {}})
        if form.get("armB"):
            arms.append({"label": "B", "arm": "sheep", "parameters": json.loads(form.get("armBParameters") or "{}")})
        if form.get("armC"):
            arms.append({"label": "C", "arm": "control", "parameters": {}})
        if not arms:
            raise ValueError("choose at least one arm")
        repeats = max(1, min(50, int(form.get("repeats") or 1)))
        scenarioId = int(form["scenarioId"])
        sheepModelId = int(form["sheepModelId"])
        visitorModelId = int(form.get("visitorModelId") or sheepModelId)
        embedModelId = int(form["embedModelId"]) if form.get("embedModelId") else None
        experimentId = self.experiments.create(scenarioId, form.get("name", "").strip(), form.get("note", "").strip(),
                                               arms, repeats, sheepModelId, visitorModelId, embedModelId)
        for iteration in range(repeats):
            for arm in arms:
                self.starter.create(scenarioId, arm["arm"], sheepModelId, visitorModelId, embedModelId, experimentId,
                                    arm["label"], iteration, arm["parameters"])
        return experimentId
