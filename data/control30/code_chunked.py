"""Blind coding by the local coder for experiments too large for one call (90 lives): the same service's logic, the runs of all
arms shuffled together, then cut into chunks that fit the coder's context (by characters), each chunk one call; the labels are
merged and stored once per coding. Usage: code_chunked.py <coderModelId> <exp:coding,coding ...>"""
import sys, random, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
from research.domains.experiments.BlindCodingContext import BlindCodingContext
app = application(root)
experiments = repositoryExperiments(app.database)
svc = serviceCodeBlind(app)
coderId = int(sys.argv[1]); LIMIT_CHARS = 52000
coder = svc.connect.processor(coderId)
for spec in sys.argv[2:]:
    eid, ids = spec.split(":"); eid = int(eid); experiment = experiments.get(eid)
    runs = [run for run in svc.runs.forExperiment(eid) if run["status"] == "done"]
    for codingId in [int(x) for x in ids.split(",")]:
        coding = svc.codings.get(codingId)
        items = [(run["id"], svc._replies(run["id"], coding)) for run in runs]
        items = [(runId, text) for runId, text in items if text]
        random.Random(eid * 1000 + codingId).shuffle(items)
        chunks, cur, size = [], [], 0
        for it in items:
            if cur and size + len(it[1]) > LIMIT_CHARS:
                chunks.append(cur); cur, size = [], 0
            cur.append(it); size += len(it[1])
        if cur: chunks.append(cur)
        labels = {}
        for chunk in chunks:
            context = BlindCodingContext(coding, [text for _, text in chunk])
            answer = coder.chat(context.system(), context.user(), svc.temperature, context.responseFormat(), purpose="coding")
            codes = svc._codes(coder, answer)
            labels.update({runId: codes.get(str(index)) for index, (runId, _) in enumerate(chunk)})
        svc.codes.replace(eid, codingId, coderId, labels)
        print(f"exp {eid} coding {codingId} '{coding['name']}': {len(items)} runs in {len(chunks)} chunks, labelled {sum(1 for v in labels.values() if v)}", flush=True)
print("done")
