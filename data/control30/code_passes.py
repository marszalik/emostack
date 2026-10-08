"""Three blind passes of the local coder over the same experiment with three different shufflings and chunkings; the label
of a run is the majority of its three labels (a tie goes to the first pass). Every pass is kept in passes_<exp>_<coding>.json
so that the coder's stability can be read. Usage: code_passes.py <coderModelId> <exp:coding,coding ...>"""
import sys, random, json, collections
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
from research.domains.experiments.BlindCodingContext import BlindCodingContext
app = application(root); experiments = repositoryExperiments(app.database); svc = serviceCodeBlind(app)
coderId = int(sys.argv[1]); LIMIT_CHARS = 52000; PASSES = 3
coder = svc.connect.processor(coderId)
for spec in sys.argv[2:]:
    eid, ids = spec.split(":"); eid = int(eid)
    runs = [run for run in svc.runs.forExperiment(eid) if run["status"] == "done"]
    for codingId in [int(x) for x in ids.split(",")]:
        coding = svc.codings.get(codingId)
        base = [(run["id"], svc._replies(run["id"], coding)) for run in runs]
        base = [(r, t) for r, t in base if t]
        passes = []
        for k in range(PASSES):
            items = base[:]; random.Random(eid * 1000 + codingId + 101 * k).shuffle(items)
            chunks, cur, size = [], [], 0
            for it in items:
                if cur and size + len(it[1]) > LIMIT_CHARS: chunks.append(cur); cur, size = [], 0
                cur.append(it); size += len(it[1])
            if cur: chunks.append(cur)
            labels = {}
            for chunk in chunks:
                ctx = BlindCodingContext(coding, [t for _, t in chunk])
                answer = coder.chat(ctx.system(), ctx.user(), svc.temperature, ctx.responseFormat(), purpose="coding")
                codes = svc._codes(coder, answer)
                labels.update({r: codes.get(str(i)) for i, (r, _) in enumerate(chunk)})
            passes.append(labels)
        final = {}
        for r, _ in base:
            votes = [p.get(r) for p in passes if p.get(r)]
            if not votes: final[r] = None; continue
            cnt = collections.Counter(votes); top = cnt.most_common(1)[0][1]
            final[r] = passes[0].get(r) if list(cnt.values()).count(top) > 1 and passes[0].get(r) in cnt else cnt.most_common(1)[0][0]
        svc.codes.replace(eid, codingId, coderId, final)
        json.dump({"passes": [{str(k): v for k, v in p.items()} for p in passes], "final": {str(k): v for k, v in final.items()}},
                  open(f"{root}/data/control30/passes_{eid}_{codingId}.json", "w"), indent=1)
        agree = sum(1 for r, _ in base if len(set(p.get(r) for p in passes)) == 1)
        print(f"exp {eid} coding {codingId} '{coding['name']}': {len(base)} runs, unanimous in {agree}", flush=True)
print("done")
