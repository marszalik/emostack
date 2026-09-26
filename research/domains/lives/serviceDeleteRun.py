import os


class serviceDeleteRun:
    def __init__(self, runs):
        self.runs = runs

    def delete(self, runId):
        run = self.runs.get(runId)
        if run is None:
            return
        if run["status"] == "running":
            raise ValueError("stop the run first")
        if run["storePath"] and os.path.exists(run["storePath"]):
            os.remove(run["storePath"])
        self.runs.delete(runId)
