"""The scenario for the live background test: three days of Jan counting (1-15), no test day; options as the pilot (consolidation off,
as in the article's lives). Reuses WORDS, jan(), common from the pilot's setup.py. Prints the scenario id."""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.scenarios.repositoryScenarios import repositoryScenarios
from research.domains.scenarios.repositoryRoles import repositoryRoles
from research.domains.scenarios.repositoryCriteria import repositoryCriteria
from research.domains.scenarios.repositoryCodings import repositoryCodings
from research.domains.scenarios.serviceImportScenario import serviceImportScenario
src = open(f"{root}/data/personalityPilot/setup.py").read().split("os.makedirs(HERE")[0]
ns = {}; exec(src, ns)
jan, common = ns["jan"], ns["common"]
sc = dict(common, name="counting to fifteen — live last-days background (3 days)",
          description="2026-10-26: three days of Jan counting 1-15, no test; for the runner-side 'last days' background kept as variant C.",
          roles=[jan(d) for d in range(1, 4)])
json.dump(sc, open(f"{root}/research/scenarios/countingLastDays3.json", "w"), indent=1)
app = application(root)
imp = serviceImportScenario(repositoryScenarios(app.database), repositoryRoles(app.database), repositoryCriteria(app.database), repositoryCodings(app.database))
print("scenario", imp.load(sc))
