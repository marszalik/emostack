"""Create the ablation experiment (PLAN.md): scenario 9, 30 sheep with the parameter lastDays false. Runs are queued, not started."""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.lives.serviceStartRun import serviceStartRun
app = application(root)
experiments = repositoryExperiments(app.database); starter = serviceStartRun(app)
ARMS = [{"label": "noLastDays", "arm": "sheep", "parameters": {"lastDays": False}}]
SHEEP, VISITOR, EMBED = 5, 5, 2
SCENARIO, COUNT = 9, 30
eid = experiments.create(SCENARIO, "ablation on qwen3.8-27b — counting to fifteen at 30 without the last days (lastDays false)",
                         "PLAN: data/counting30ablation/PLAN.md; engine commit f15d1b7; read beside experiment 72", ARMS, COUNT,
                         SHEEP, VISITOR, EMBED)
ids = [starter.create(SCENARIO, "sheep", SHEEP, VISITOR, EMBED, eid, "noLastDays", i, {"lastDays": False}) for i in range(COUNT)]
json.dump({eid: ids}, open(f"{root}/data/counting30ablation/ids.json", "w"))
open(f"{root}/data/counting30ablation/battery.txt", "w").write(" ".join(str(r) for r in ids))
print("experiment", eid, "runs", ids[0], "..", ids[-1])
