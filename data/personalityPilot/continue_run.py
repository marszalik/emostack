"""Continue a finished life with one more visit: a new run on a one-role scenario, started on a COPY of the old run's store, with a
night (gap, forgetting, consolidation as the scenario says) before the visitor comes. The engine's runner removes an existing store and
replays the seeds; this runner keeps the store and skips the seeds, everything else is the panel's own.
Usage: continue_run.py <oldRunId> <scenarioId> <sheepModelId> <visitorModelId> <embedModelId> <experimentName>"""
import sys, os, shutil
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.serviceStartRun import serviceStartRun
from research.domains.lives.serviceRunSheep import serviceRunSheep
from research.domains.lives.serviceVisitorLine import serviceVisitorLine
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.scenarios.ScenarioOptions import ScenarioOptions
from emostack.core.timeSource import timeSource
from emostack.core.config import config
from emostack.runtime.engine import engine
import research.domains.lives.serviceRunSheep as srs

oldRun, scenarioId, sheepModel, visitorModel, embedModel = [int(x) for x in sys.argv[1:6]]; name = sys.argv[6]
app = application(root); runs = repositoryRuns(app.database); starter = serviceStartRun(app)
experiments = repositoryExperiments(app.database)
eid = experiments.create(scenarioId, name, f"continuation of run {oldRun} on its own store; one more visit after a night",
                         [{"label": "A", "arm": "sheep", "parameters": {}}], 1, sheepModel, visitorModel, embedModel)
rid = starter.create(scenarioId, "sheep", sheepModel, visitorModel, embedModel, eid, "A", 0, {})
old = runs.get(oldRun); newStore = os.path.join(app.config.storesFolder, f"run{rid}.db")
shutil.copyfile(old["storePath"], newStore)
print("experiment", eid, "run", rid, "store copied from", old["storePath"], flush=True)

class continuingSheep(serviceRunSheep):
    def run(self, runId, scenario, roles, processor, embedder, visitorProcessor, storePath):
        options = ScenarioOptions(scenario["options"])
        clock = timeSource()
        mind = engine(config({"databasePath": storePath, "parameters": options.parameters}), processor=processor, embedder=embedder, time=clock)
        self.runId = runId; self.sheepCalls = srs.CallLog(processor); self.visitorCalls = srs.CallLog(visitorProcessor)
        being = scenario["beingName"]
        try:
            turnIndex = 0
            for day, role in enumerate(roles):
                self._night(mind, clock, being, role, options, day)   # a night before every visit, the first included
                turnIndex = self._day(mind, being, role, day, turnIndex)
        finally:
            mind.close()

# run it the panel's way, but with the continuing runner
run = runs.get(rid); scenario = starter.scenarios.get(scenarioId); roles = starter.roles.forScenario(scenarioId)
scenario["options"]["parameters"] = dict(scenario["options"].get("parameters", {}))
runs.setSettings(rid, {"scenario": scenario, "roles": roles, "armParameters": {}, "continuationOf": oldRun}, newStore)
runs.setStatus(rid, "running")
try:
    visitor = starter.models.processor(visitorModel)
    import threading
    continuingSheep(starter.turns, app.streams, serviceVisitorLine(visitor), threading.Event()).run(
        rid, scenario, roles, starter.models.processor(sheepModel), starter.models.embedder(embedModel), visitor, newStore)
    runs.setStatus(rid, "done"); print("done", rid, flush=True)
except Exception as e:
    import traceback; runs.setStatus(rid, "error", f"{e}\n{traceback.format_exc()}"[:6000]); print("ERROR", e, flush=True); raise
