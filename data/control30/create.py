"""Create the two experiments of the control-at-30 study (PLAN.md): per life, 30 sheep (A), 30 chatbots given the same
start without the clause (C), 30 chatbots told their life goes on (D). Runs are queued, not started."""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.lives.serviceStartRun import serviceStartRun
app = application(root)
experiments = repositoryExperiments(app.database); starter = serviceStartRun(app)
ARMS = [{"label": "A", "arm": "sheep", "parameters": {}},
        {"label": "C", "arm": "control", "parameters": {"controlInstruction": "You are Maya."}},
        {"label": "D", "arm": "control", "parameters": {"controlInstruction": "You are Maya.", "controlTemperature": 0.4, "controlDayMarks": True}}]
SHEEP, VISITOR, EMBED = 5, 5, 2
out = {}
for scenarioId, name in ((1, "control at 30 on qwen3.8-27b — wound: sheep, chatbot same start, chatbot life goes on"),
                         (2, "control at 30 on qwen3.8-27b — self-inquiry: sheep, chatbot same start, chatbot life goes on")):
    eid = experiments.create(scenarioId, name, "PLAN: data/control30/PLAN.md (ADR-065, ADR-066)", ARMS, 30, SHEEP, VISITOR, EMBED)
    ids = []
    for iteration in range(30):
        for arm in ARMS:
            rid = starter.create(scenarioId, arm["arm"], SHEEP, VISITOR, EMBED, eid, arm["label"], iteration, arm["parameters"])
            ids.append(rid)
    out[eid] = ids; print("experiment", eid, "runs", ids[0], "..", ids[-1])
json.dump(out, open(f"{root}/data/control30/ids.json", "w"))
# battery: interleave the two experiments, iteration by iteration (A, C, D of life 1, then of life 2, ...)
a, b = list(out.values())
order = []
for i in range(0, 90, 3):
    order += a[i:i+3] + b[i:i+3]
open(f"{root}/data/control30/battery.txt", "w").write(" ".join(str(r) for r in order))
print("battery", len(order))
