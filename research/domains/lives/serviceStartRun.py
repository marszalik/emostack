import os
import threading
import traceback

from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.repositoryTurns import repositoryTurns
from research.domains.lives.serviceRunControl import serviceRunControl
from research.domains.lives.serviceRunSheep import serviceRunSheep
from research.domains.lives.serviceVisitorLine import serviceVisitorLine
from research.domains.lives.stopSignals import stopSignals
from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceConnectModel import serviceConnectModel
from research.domains.scenarios.repositoryRoles import repositoryRoles
from research.domains.scenarios.repositoryScenarios import repositoryScenarios


class serviceStartRun:
    """Creates a run of one arm of a scenario and runs it: in the background for a single run, in
    the caller's thread for an experiment, which runs its lives one after another."""

    def __init__(self, application):
        self.application = application
        database = application.database
        self.runs = repositoryRuns(database)
        self.turns = repositoryTurns(database)
        self.scenarios = repositoryScenarios(database)
        self.roles = repositoryRoles(database)
        self.models = serviceConnectModel(repositoryModels(database), application.config.root)

    def create(self, scenarioId, arm, sheepModelId, visitorModelId, embedModelId, experimentId=None,
               armLabel="", iteration=0, armParameters=None):
        scenario = self.scenarios.get(scenarioId)
        if scenario is None:
            raise ValueError(f"no scenario {scenarioId}")
        if not self.roles.forScenario(scenarioId):
            raise ValueError("the scenario has no visitors")
        if arm == "sheep" and not embedModelId:
            raise ValueError("a being needs an embedder")
        return self.runs.create(scenarioId, arm, sheepModelId, visitorModelId or sheepModelId,
                                embedModelId if arm == "sheep" else None, experimentId, armLabel, iteration,
                                {"armParameters": armParameters or {}})

    def startInBackground(self, runId):
        threading.Thread(target=self.run, args=(runId,), daemon=True).start()

    def run(self, runId):
        run = self.runs.get(runId)
        key = f"run:{runId}"
        stop = stopSignals().signal(key)
        streams = self.application.streams
        scenario = self.scenarios.get(run["scenarioId"])
        armParameters = run["settings"].get("armParameters", {})
        scenario["options"]["parameters"] = dict(scenario["options"].get("parameters", {}), **armParameters)
        roles = self.roles.forScenario(run["scenarioId"])
        storePath = os.path.join(self.application.config.storesFolder, f"run{runId}.db")
        self.runs.setSettings(runId, {"scenario": scenario, "roles": roles, "armParameters": armParameters},
                              storePath if run["arm"] == "sheep" else "")
        self.runs.setStatus(runId, "running")
        streams.emit(key, {"kind": "status", "text": f"{run['arm']} run started"})
        try:
            visitor = self.models.processor(run["visitorModelId"])
            visitorLine = serviceVisitorLine(visitor)
            if run["arm"] == "sheep":
                serviceRunSheep(self.turns, streams, visitorLine, stop).run(
                    runId, scenario, roles, self.models.processor(run["sheepModelId"]),
                    self.models.embedder(run["embedModelId"]), visitor, storePath)
            else:
                serviceRunControl(self.turns, streams, visitorLine, stop).run(
                    runId, scenario, roles, self.models.processor(run["sheepModelId"]), visitor)
            status = "stopped" if stop.is_set() else "done"
            self.runs.setStatus(runId, status)
            streams.emit(key, {"kind": "done", "text": status})
        except Exception as error:
            self.runs.setStatus(runId, "error", f"{error}\n{traceback.format_exc()}"[:6000])
            streams.emit(key, {"kind": "error", "text": str(error)})
        finally:
            stopSignals().forget(key)
