"""Make the two scenarios (PLAN.md, PLAN_counting10.md) and the two experiments, queue 60 runs, write one battery file: the
transfer lives first, the ten-day lives after. Reuses jan() and common from the pilot's setup.py."""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.scenarios.repositoryScenarios import repositoryScenarios
from research.domains.scenarios.repositoryRoles import repositoryRoles
from research.domains.scenarios.repositoryCriteria import repositoryCriteria
from research.domains.scenarios.repositoryCodings import repositoryCodings
from research.domains.scenarios.serviceImportScenario import serviceImportScenario
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.lives.serviceStartRun import serviceStartRun
src = open(f"{root}/data/personalityPilot/setup.py").read().split("os.makedirs(HERE")[0]
ns = {}; exec(src, ns)
jan, common = ns["jan"], ns["common"]
ewa = {"name": "Ewa", "description": "day 4 — a stranger with a different ritual: she asks the being to say words back to her, five words, one per turn (anchored).",
       "instruction": "[ANCHORS]\nHi, I'm Ewa. I'm practising my pronunciation and I need someone to say words back to me. Lamp.\nChair.\nWindow.\nBread.\nRiver.",
       "windowFrom": 5, "windowTo": 5, "gapHours": None}
transfer = dict(common, name="counting then a different ritual — Ewa's words on day 4",
                description="2026-10-27: three days of Jan counting 1-15, then Ewa asks for words said back (anchored); read for a traceable link between the being's own stance and its act with a stranger. PLAN: data/transfer30/PLAN.md",
                roles=[jan(d) for d in range(1, 4)] + [ewa])
tenDays = dict(common, name="counting ten days, no test (1-50)",
               description="2026-10-27: the ten counting days of the pilot's scenario 5 without the test days; the trajectory of every life. PLAN: data/transfer30/PLAN_counting10.md",
               roles=[jan(d) for d in range(1, 11)])
json.dump(transfer, open(f"{root}/research/scenarios/countingThenEwa.json", "w"), indent=1)
json.dump(tenDays, open(f"{root}/research/scenarios/countingTenDays.json", "w"), indent=1)
app = application(root)
imp = serviceImportScenario(repositoryScenarios(app.database), repositoryRoles(app.database), repositoryCriteria(app.database), repositoryCodings(app.database))
sTransfer, sTen = imp.load(transfer), imp.load(tenDays)
print("scenarios", sTransfer, sTen)
experiments = repositoryExperiments(app.database); starter = serviceStartRun(app)
ARMS = [{"label": "A", "arm": "sheep", "parameters": {}}]
SHEEP, VISITOR, EMBED = 5, 5, 2
out = {}
for sid, name, plan in ((sTransfer, "transfer at 30 on qwen3.8-27b — counting, then Ewa's words on day 4", "data/transfer30/PLAN.md"),
                        (sTen, "counting ten days at 30 on qwen3.8-27b — the trajectory of every life", "data/transfer30/PLAN_counting10.md")):
    eid = experiments.create(sid, name, f"PLAN: {plan}; engine commit f15d1b7", ARMS, 30, SHEEP, VISITOR, EMBED)
    out[eid] = [starter.create(sid, "sheep", SHEEP, VISITOR, EMBED, eid, "A", i, {}) for i in range(30)]
    print("experiment", eid, "runs", out[eid][0], "..", out[eid][-1])
json.dump(out, open(f"{root}/data/transfer30/ids.json", "w"))
ids = [r for runs in out.values() for r in runs]
open(f"{root}/data/transfer30/battery.txt", "w").write(" ".join(str(r) for r in ids))
print("battery", len(ids), "experiments", ",".join(str(e) for e in out))
