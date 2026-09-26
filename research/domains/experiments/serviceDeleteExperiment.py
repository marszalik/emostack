from research.domains.lives.serviceDeleteRun import serviceDeleteRun


class serviceDeleteExperiment:
    def __init__(self, experiments, runs):
        self.experiments = experiments
        self.runs = runs

    def delete(self, experimentId):
        experiment = self.experiments.get(experimentId)
        if experiment and experiment["status"] == "running":
            raise ValueError("stop the experiment first")
        for run in self.runs.forExperiment(experimentId):
            serviceDeleteRun(self.runs).delete(run["id"])
        self.experiments.delete(experimentId)
