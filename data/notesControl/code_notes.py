"""Blind coding of notes-control experiments 34, 35 (qwen3.8-27b) by the panel's own coder (one call per coding over every finished
run of the experiment, arms hidden, order shuffled), for both coders, then the counts and Fisher's p."""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.experiments.repositoryCodes import repositoryCodes
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
from research.domains.experiments.serviceCodingResults import serviceCodingResults
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.models.repositoryModels import repositoryModels
from research.domains.scenarios.repositoryCodings import repositoryCodings
app = application(root)
experiments = repositoryExperiments(app.database)
coder = serviceCodeBlind(app)
CODINGS = {34: [1], 35: [2, 3, 4, 5]}
if "--results" not in sys.argv:
    for eid, codingIds in CODINGS.items():
        for coderId in (3, 4):
            coder.code(experiments.get(eid), coderId, codingIds)
            print(f"coded experiment {eid} with coder {coderId}", flush=True)
results = serviceCodingResults(repositoryRuns(app.database), repositoryCodes(app.database),
                               repositoryCodings(app.database), repositoryModels(app.database))
out = {eid: results.results(experiments.get(eid)) for eid in CODINGS}
json.dump(out, open(f"{root}/data/notesControl/coding_results_notes.json", "w"), indent=1, default=str)
for eid, rows in out.items():
    for row in rows:
        print(eid, json.dumps(row, default=str)[:400])
