"""Blind coding by a local coder (panel model id given as the first argument) of the experiments and codings listed, to
compare with the paid coders and the hand labels. Usage: code_local.py <coderModelId> <exp:coding,coding ...>"""
import sys, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
app = application(root)
experiments = repositoryExperiments(app.database)
coder = serviceCodeBlind(app)
coderId = int(sys.argv[1])
for spec in sys.argv[2:]:
    eid, ids = spec.split(":")
    coder.code(experiments.get(int(eid)), coderId, [int(x) for x in ids.split(",")])
    print(f"coded experiment {eid} codings {ids} with coder {coderId}", flush=True)
