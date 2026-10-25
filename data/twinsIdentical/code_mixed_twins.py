"""Blind coding of the identical twins, populations A (experiment 57) and B (58), in ONE shuffled list per coding, so that the
coder's list effect does not separate them; three passes, majority of three, ties to the first pass. Nothing is written to the
codes table. Copied from ablations2/code_mixed2.py, two arms instead of three, the arm read from the experiment, not the label.
Usage: code_mixed_twins.py <coderModelId> <expA:expB:coding,coding ...>"""
import sys, random, json, collections
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
from research.domains.experiments.BlindCodingContext import BlindCodingContext
app = application(root); svc = serviceCodeBlind(app)
coderId = int(sys.argv[1]); LIMIT_CHARS = 52000; PASSES = 3
coder = svc.connect.processor(coderId)
outPath = f"{root}/data/twinsIdentical/mixed_coding.json"
try:
    out = json.load(open(outPath))
except Exception:
    out = {}
for spec in sys.argv[2:]:
    ea, eb, ids = spec.split(":"); ea, eb = int(ea), int(eb)
    runs = [r for r in svc.runs.forExperiment(ea) if r["status"] == "done"] + \
           [r for r in svc.runs.forExperiment(eb) if r["status"] == "done"]
    armOf = {r["id"]: ("A" if r["experimentId"] == ea else "B") for r in runs}
    for codingId in [int(x) for x in ids.split(",")]:
        coding = svc.codings.get(codingId)
        base = [(r["id"], svc._replies(r["id"], coding)) for r in runs]
        base = [(r, t) for r, t in base if t]
        passes = []
        for k in range(PASSES):
            items = base[:]; random.Random(7000 + ea * 1000 + codingId + 101 * k).shuffle(items)
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
        byArm = {a: dict(collections.Counter(v for r, v in final.items() if armOf[r] == a)) for a in ("A", "B")}
        agree = sum(1 for r, _ in base if len(set(p.get(r) for p in passes)) == 1)
        out[f"{ea}_{eb}_{codingId}"] = {"byArm": byArm, "final": {str(k): v for k, v in final.items()},
                                        "armOf": {str(k): v for k, v in armOf.items()},
                                        "passes": [{str(k): v for k, v in p.items()} for p in passes]}
        print(f"{ea}/{eb} coding {codingId} '{coding['name']}': {byArm}  unanimous {agree}/{len(base)}", flush=True)
        json.dump(out, open(outPath, "w"), indent=1)
print("done")
