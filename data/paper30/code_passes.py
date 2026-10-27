"""Three blind passes of the local coder over the sheep with the last days (a new experiment) and the sheep without them (the
sheep arm of the experiment of 7 October), in ONE shuffled list, three shufflings and chunkings; the label of a run is the
majority of its three labels (a tie goes to the first pass). Every pass is kept in passes_<new>_<old>_<coding>.json; the final
labels of the NEW experiment go to the panel's codes; the old experiment's codes of 8 October are left as they are.
Usage: code_passes.py <coderModelId> <newExp>:<oldExp>:<coding,coding ...>   e.g. 8 73:38:1,14,16 74:39:2,15,3,4,5"""
import sys, random, json, collections
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
from research.domains.experiments.BlindCodingContext import BlindCodingContext
app = application(root); svc = serviceCodeBlind(app)
coderId = int(sys.argv[1]); LIMIT_CHARS = 52000; PASSES = 3
coder = svc.connect.processor(coderId)
for spec in sys.argv[2:]:
    new, old, ids = spec.split(":"); new, old = int(new), int(old)
    runs = [run for run in svc.runs.forExperiment(new) if run["status"] == "done"]
    runs += [run for run in svc.runs.forExperiment(old) if run["status"] == "done" and run["arm"] == "sheep" and run["armLabel"] == "A"]
    print(f"experiments {new} + {old}(A): {len(runs)} lives", flush=True)
    for codingId in [int(x) for x in ids.split(",")]:
        coding = svc.codings.get(codingId)
        base = [(run["id"], svc._replies(run["id"], coding)) for run in runs]
        base = [(r, t) for r, t in base if t]
        passes = []
        for k in range(PASSES):
            items = base[:]; random.Random(new * 1000 + codingId + 101 * k).shuffle(items)
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
        newIds = {run["id"] for run in svc.runs.forExperiment(new)}
        svc.codes.replace(new, codingId, coderId, {r: v for r, v in final.items() if r in newIds})
        json.dump({"passes": [{str(k): v for k, v in p.items()} for p in passes], "final": {str(k): v for k, v in final.items()},
                   "new": sorted(newIds)}, open(f"{root}/data/paper30/passes_{new}_{old}_{codingId}.json", "w"), indent=1)
        agree = sum(1 for r, _ in base if len(set(p.get(r) for p in passes)) == 1)
        counts = {arm: collections.Counter(final[r] for r, _ in base if (r in newIds) == (arm == "with")) for arm in ("with", "without")}
        print(f"coding {codingId} '{coding['name']}': {len(base)} lives, unanimous in {agree}; with the last days {dict(counts['with'])}; "
              f"without {dict(counts['without'])}", flush=True)
print("done")
