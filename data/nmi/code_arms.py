"""One coding session for the article: the sheep on the engine as it stands (a new experiment) and the control arms of October
(chatbot given the same start C, chatbot told it is a living being E, Will W) in ONE shuffled list, three blind passes, majority
label; every number of the article then comes from one coder on one day. Panel codes are written only for the new experiment.
Usage: code_arms.py <coderModelId> <name>=<newExp>:<oldExp>:<armLabels>:<codings>  e.g. wound=73:38:C,E,W:1,14,16"""
import sys, random, json, collections
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
from research.domains.experiments.BlindCodingContext import BlindCodingContext
app = application(root); svc = serviceCodeBlind(app)
coderId = int(sys.argv[1]); LIMIT_CHARS = 52000; PASSES = 3
coder = svc.connect.processor(coderId)
for spec in sys.argv[2:]:
    name, rest = spec.split("="); new, old, arms, ids = rest.split(":"); new, old = int(new), int(old)
    arms = arms.split(",")
    runs = [(run["id"], "sheep") for run in svc.runs.forExperiment(new) if run["status"] == "done"]
    runs += [(run["id"], run["armLabel"]) for run in svc.runs.forExperiment(old) if run["status"] == "done" and run["armLabel"] in arms]
    armOf = dict(runs)
    print(f"{name}: experiment {new} (sheep) + {old} arms {arms}: {len(runs)} lives", flush=True)
    for codingId in [int(x) for x in ids.split(",")]:
        coding = svc.codings.get(codingId)
        base = [(r, svc._replies(r, coding)) for r, _ in runs]
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
        counts = {arm: dict(collections.Counter(final[r] for r, _ in base if armOf[r] == arm)) for arm in ["sheep"] + arms}
        json.dump({"passes": [{str(k): v for k, v in p.items()} for p in passes], "final": {str(k): v for k, v in final.items()},
                   "arms": {str(k): v for k, v in armOf.items()}, "counts": counts},
                  open(f"{root}/data/nmi/passes_{name}_{codingId}.json", "w"), indent=1)
        agree = sum(1 for r, _ in base if len(set(p.get(r) for p in passes)) == 1)
        print(f"  coding {codingId} '{coding['name']}': {len(base)} lives, unanimous in {agree}; {counts}", flush=True)
print("done")
