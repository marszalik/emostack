from research.domains.lives.stopSignals import stopSignals


class serviceStopExperiment:
    """Stops the life that is running and leaves the queued ones unrun."""

    def __init__(self, runs):
        self.runs = runs

    def stop(self, experimentId):
        stopSignals().stop(f"experiment:{experimentId}")
        for run in self.runs.forExperiment(experimentId):
            if run["status"] == "running":
                stopSignals().stop(f"run:{run['id']}")
