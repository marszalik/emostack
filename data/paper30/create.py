"""Create the two experiments of the paper's lives at 30 on the engine with the last days (PLAN.md): scenario 1 (wound) and 2
(sceptic), one arm, 30 sheep each. Runs are queued, not started; the battery interleaves the two lives."""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.lives.serviceStartRun import serviceStartRun
app = application(root)
experiments = repositoryExperiments(app.database); starter = serviceStartRun(app)
ARMS = [{"label": "A", "arm": "sheep", "parameters": {}}]
SHEEP, VISITOR, EMBED = 5, 5, 2
out = {}
for scenarioId, name in ((1, "wound at 30 on qwen3.8-27b — the last days in the engine"),
                         (2, "self-inquiry at 30 on qwen3.8-27b — the last days in the engine")):
    eid = experiments.create(scenarioId, name, "PLAN: data/paper30/PLAN.md; engine commit ee1d13d (the last days beside the focus)",
                             ARMS, 30, SHEEP, VISITOR, EMBED)
    out[eid] = [starter.create(scenarioId, "sheep", SHEEP, VISITOR, EMBED, eid, "A", iteration, {}) for iteration in range(30)]
    print("experiment", eid, "runs", out[eid][0], "..", out[eid][-1])
json.dump(out, open(f"{root}/data/paper30/ids.json", "w"))
a, b = list(out.values())
order = [r for pair in zip(a, b) for r in pair]
open(f"{root}/data/paper30/battery.txt", "w").write(" ".join(str(r) for r in order))
print("battery", len(order), "experiments", ",".join(str(e) for e in out))
