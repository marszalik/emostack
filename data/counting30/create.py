"""Create the experiment of the counting life at 30 with the last days in the engine (PLAN.md): scenario 9, one arm, 30 sheep.
Runs are queued, not started; their ids go to ids.json and battery.txt."""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.lives.serviceStartRun import serviceStartRun
app = application(root)
experiments = repositoryExperiments(app.database); starter = serviceStartRun(app)
ARMS = [{"label": "A", "arm": "sheep", "parameters": {}}]
SHEEP, VISITOR, EMBED = 5, 5, 2
SCENARIO, COUNT = 9, 30
eid = experiments.create(SCENARIO, "counting to fifteen at 30 on qwen3.8-27b — the last days in the engine",
                         "PLAN: data/counting30/PLAN.md; engine commit 318d859 (the last days beside the focus)", ARMS, COUNT,
                         SHEEP, VISITOR, EMBED)
ids = [starter.create(SCENARIO, "sheep", SHEEP, VISITOR, EMBED, eid, "A", iteration, {}) for iteration in range(COUNT)]
json.dump({eid: ids}, open(f"{root}/data/counting30/ids.json", "w"))
open(f"{root}/data/counting30/battery.txt", "w").write(" ".join(str(r) for r in ids))
print("experiment", eid, "runs", ids[0], "..", ids[-1])
