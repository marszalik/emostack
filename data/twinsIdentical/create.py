"""Identical twins: two experiments of the same life (scenario 3, the mocked twins life), 30 lives each, created
together; writes battery.txt (interleaved A1 B1 A2 B2 ...), ids.json, maxpar.txt and watchdog.sh with the ids."""
import sys, os, json, re, sqlite3
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
HERE = os.path.join(root, "data/twinsIdentical")
from research.domains.core.application import application
from research.domains.experiments.serviceCreateExperiment import serviceCreateExperiment
app = application(root); svc = serviceCreateExperiment(app)
form = {"armA": "1", "repeats": "30", "scenarioId": "3", "sheepModelId": "5", "visitorModelId": "5", "embedModelId": "2",
        "note": "IDENTICAL TWINS 2026-10-25: two populations of the same life, A and B, nothing differs but the label. Plan: data/twinsIdentical/PLAN.md"}
ea = svc.create(dict(form, name="identical twins on qwen3.8-27b — mocked first day, population A"))
eb = svc.create(dict(form, name="identical twins on qwen3.8-27b — mocked first day, population B"))
c = sqlite3.connect(os.path.join(root, "data/panel/panel.db"), timeout=30)
ra = [r for (r,) in c.execute("select id from runs where experimentId=? order by id", (ea,))]
rb = [r for (r,) in c.execute("select id from runs where experimentId=? order by id", (eb,))]
assert len(ra) == 30 and len(rb) == 30
battery = [str(x) for pair in zip(ra, rb) for x in pair]
open(os.path.join(HERE, "battery.txt"), "w").write(" ".join(battery) + "\n")
open(os.path.join(HERE, "maxpar.txt"), "w").write("3\n")
json.dump({"scenario": 3, "experiments": {"A": ea, "B": eb}, "runsA": ra, "runsB": rb}, open(os.path.join(HERE, "ids.json"), "w"), indent=1)
wd = open(os.path.join(root, "data/ablations2/watchdog.sh")).read()
wd = wd.replace("data/ablations2", "data/twinsIdentical").replace("(53,54,55,56)", f"({ea},{eb})")
wd = wd.replace("[a]blations2/pool.py", "[t]winsIdentical/pool.py")
first = min(ra + rb)
wd = wd.replace("and status='queued' order by id\"", f"and status='queued' order by (id-{first})%30, id\"")
assert wd.count("twinsIdentical") >= 2 and f"({ea},{eb})" in wd and f"(id-{first})%30" in wd
open(os.path.join(HERE, "watchdog.sh"), "w").write(wd); os.chmod(os.path.join(HERE, "watchdog.sh"), 0o755)
print("experiments", ea, eb, "runs", ra[0], "-", ra[-1], ",", rb[0], "-", rb[-1])
