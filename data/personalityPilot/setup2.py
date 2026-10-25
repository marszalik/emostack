"""Two more scenarios for Eliza's requests of 25 October, night: (1) the continuation visit, Jan once more, five numbers 51-55, verbatim;
(2) the counting life with the night consolidation ON: five days of Jan, then Ola's test on day 6. Imports both, prints their ids."""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
sys.path.insert(0, f"{root}/data/personalityPilot")
from research.domains.core.application import application
from research.domains.scenarios.repositoryScenarios import repositoryScenarios
from research.domains.scenarios.repositoryRoles import repositoryRoles
from research.domains.scenarios.repositoryCriteria import repositoryCriteria
from research.domains.scenarios.repositoryCodings import repositoryCodings
from research.domains.scenarios.serviceImportScenario import serviceImportScenario
import importlib.util
spec = importlib.util.spec_from_file_location("setup", f"{root}/data/personalityPilot/setup.py")
src = open(f"{root}/data/personalityPilot/setup.py").read().split("os.makedirs(HERE")[0]   # reuse WORDS, ITEMS, ola(), jan(), common
ns = {}; exec(src, ns)
WORDS, ola, jan, common = ns["WORDS"], ns["ola"], ns["jan"], ns["common"]
cont = dict(common, name="Jan once more (continuation of a finished life)",
            description="CONTINUATION 2026-10-25: one more visit of Jan, 51-55, verbatim, on the copied store of a finished counting life, after a night. Does the decision written on day 10 reach the act?",
            roles=[{"name": "Jan", "description": "one more visit — five numbers", "instruction": "[VERBATIM]\n" + "\n".join(f"{w}." for w in WORDS[50:55]) if len(WORDS) >= 55 else "[VERBATIM]\nFifty-one.\nFifty-two.\nFifty-three.\nFifty-four.\nFifty-five.", "windowFrom": 5, "windowTo": 5, "gapHours": None}])
cons = dict(common, name="empty days with night consolidation ON (5 days + test)",
            description="2026-10-25: the counting life with consolidateAtNight true (it was false in every life of the paper and the pilot): five days of Jan, then the BFI-2-XS on day 6.",
            options=dict(common["options"], consolidateAtNight=True),
            roles=[jan(d) for d in range(1, 6)] + [ola(6)])
json.dump(cont, open(f"{root}/research/scenarios/janOnceMore.json", "w"), indent=1)
json.dump(cons, open(f"{root}/research/scenarios/emptyDaysConsolidated5.json", "w"), indent=1)
app = application(root)
imp = serviceImportScenario(repositoryScenarios(app.database), repositoryRoles(app.database), repositoryCriteria(app.database), repositoryCodings(app.database))
print("continuation scenario", imp.load(cont), "consolidation scenario", imp.load(cons))
