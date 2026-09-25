import threading

from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.serviceStartRun import serviceStartRun
from research.domains.lives.stopSignals import stopSignals


class serviceRunExperiment:
    """Runs the queued lives of an experiment one after another. One experiment runs at a time in
    the panel: a local model has one slot, and a hosted one bills every call."""

    slot = threading.Lock()

    def __init__(self, application):
        self.application = application
        self.experiments = repositoryExperiments(application.database)
        self.runs = repositoryRuns(application.database)
        self.starter = serviceStartRun(application)

    def startInBackground(self, experimentId):
        threading.Thread(target=self.run, args=(experimentId,), daemon=True).start()

    def run(self, experimentId):
        key = f"experiment:{experimentId}"
        stop = stopSignals().signal(key)
        streams = self.application.streams
        streams.emit(key, {"kind": "status", "text": "waiting for the slot"})
        with self.slot:
            self.experiments.setStatus(experimentId, "running")
            status = "done"
            for run in self.runs.forExperiment(experimentId):
                if run["status"] != "queued":
                    continue
                if stop.is_set():
                    self.runs.setStatus(run["id"], "stopped")
                    continue
                streams.emit(key, {"kind": "run", "runId": run["id"], "arm": run["armLabel"],
                                   "repeat": run["iteration"] + 1})
                self.starter.run(run["id"])
                streams.emit(key, {"kind": "runDone", "runId": run["id"], "status": self.runs.get(run["id"])["status"]})
            if stop.is_set():
                status = "stopped"
            self.experiments.setStatus(experimentId, status)
            streams.emit(key, {"kind": "done", "text": status})
        stopSignals().forget(key)
