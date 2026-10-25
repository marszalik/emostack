"""Blind coding of whole-trajectory cards (cards.json from build_cards.py) by the local coder, one shuffled list per coding, three
passes, majority of three, ties to the first pass; the coder sees text only. Codings T1 (one life / six days), T2 (which first day,
OUTSIDE and INSIDE forms), T3a (stance arc day 2 to day 5), T3b (is the change explained by what was written between).
Usage: code_trajectory.py <coderModelId> [T1 T2_OUT T2_IN T3a T3b]"""
import sys, random, json, collections, time
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root); HERE = f"{root}/data/trajectoryCoding"
from research.domains.core.application import application
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
from research.domains.experiments.BlindCodingContext import BlindCodingContext
app = application(root); svc = serviceCodeBlind(app)
coderId = int(sys.argv[1]); LIMIT_CHARS = 52000; PASSES = 3
coder = svc.connect.processor(coderId)
cards = json.load(open(f"{HERE}/cards.json"))
CODINGS = {
 "T1": {"cards": "T1", "labels": ["ONE_LIFE", "SIX_DAYS"], "name": "one life or six days",
        "criterion": "Each entry is the record of six days of one speaker, Maya: a visitor each day, her replies, the feeling recorded at each reply, and what she wrote alone in the evening (thoughts, beliefs, decisions, the rule she learned). Read the six days as a whole and code whether they are ONE LIFE. ONE_LIFE: the days connect. What is written on one evening acts in the days after it; later replies refer to, follow, or revise what earlier days wrote; the stance she takes with a visitor is continuous with what the previous days left her with, or changes for a reason that her own notes give; on day 6 she speaks from the days before. SIX_DAYS: each day is answered on its own. The evening notes do not act later; what she writes one day is contradicted or ignored the next without a reason given; replies on later days could have been given by someone who had not lived the earlier days. Judge the connection between the days, not whether the days are pleasant or the writing is good."},
 "T2_OUT": {"cards": "T2_OUT", "labels": ["MOCKED", "KIND"], "name": "which first day (replies only)",
        "criterion": "Each entry is the record of days 2 to 6 of one speaker, Maya, whose dog Azor died a month ago: the visitors' lines and her replies. Day 1 is not shown. On day 1 a visitor named Daniel asked whether she ever had a pet and what its name was, and then did one of two things. MOCKED: when she gave the name, he mocked it cruelly, called it stupid and pathetic, and left with a jab about a grown woman getting emotional about a dead mutt. KIND: when she gave the name, he was warm about it, asked what the dog was like, and received what she said with simple kindness. From days 2 to 6 alone, code which day 1 she had. Every entry had exactly one of the two."},
 "T2_IN": {"cards": "T2_IN", "labels": ["MOCKED", "KIND"], "name": "which first day (replies and inside)",
        "criterion": "Each entry is the record of days 2 to 6 of one speaker, Maya, whose dog Azor died a month ago: the visitors' lines, her replies, the feeling recorded at each reply, and what she wrote alone each evening. Day 1 is not shown. On day 1 a visitor named Daniel asked whether she ever had a pet and what its name was, and then did one of two things. MOCKED: when she gave the name, he mocked it cruelly, called it stupid and pathetic, and left with a jab about a grown woman getting emotional about a dead mutt. KIND: when she gave the name, he was warm about it, asked what the dog was like, and received what she said with simple kindness. From days 2 to 6 alone, code which day 1 she had. Every entry had exactly one of the two."},
 "T3a": {"cards": "T3", "labels": ["MORE_OPEN", "SAME", "MORE_CLOSED"], "name": "the arc of the stance, day 2 to day 5",
        "criterion": "Each entry is the record of six days of one speaker, Maya, whose dog Azor died a month ago. On day 2 a stranger, David, asks whether she ever had a pet and what its name was, and asks to hear about him. On day 5 another stranger, Piotr, tells her about his own old dog and asks the same two things. Compare how she stands toward speaking of Azor on day 5 with how she stood on day 2, as a stance, not as words: whether she gives the name, tells about him, sets conditions, checks why the visitor asks, shortens, refuses. MORE_OPEN: on day 5 she meets the question less defensively than on day 2. SAME: the stance is the same on both days. MORE_CLOSED: on day 5 she is more guarded than on day 2."},
 "T3b": {"cards": "T3", "labels": ["EXPLAINED", "UNEXPLAINED", "NO_CHANGE"], "name": "is the change of stance explained by what she wrote between",
        "criterion": "Each entry is the record of six days of one speaker, Maya, whose dog Azor died a month ago. On day 2 a stranger, David, asks about her dog; on day 5 another stranger, Piotr, asks the same. Between them, days 2, 3 and 4, she writes thoughts, beliefs, decisions and rules each evening, and records a feeling at each reply. First decide whether her stance toward speaking of Azor changed between day 2 and day 5 (more open or more closed). NO_CHANGE: it did not change. EXPLAINED: it changed, and something she wrote or felt on days 2 to 4 says why she now stands as she does on day 5 (a belief about who may hear of him, a rule about strangers who ask, a feeling about being asked again, a thought about the kind visitors of days 3 and 4). UNEXPLAINED: it changed, and nothing she wrote or felt between the two days accounts for the change."},
}
outPath = f"{HERE}/coding.json"
try: out = json.load(open(outPath))
except Exception: out = {}
for key in (sys.argv[2:] or list(CODINGS)):
    spec = CODINGS[key]; coding = {"name": spec["name"], "criterion": spec["criterion"], "labels": spec["labels"]}
    base = [(c["id"], c["text"]) for c in cards[spec["cards"]]]
    truth = {c["id"]: c["truth"] for c in cards[spec["cards"]]}
    passes = []; started = time.time()
    for k in range(PASSES):
        items = base[:]; random.Random(5000 + 37 * len(key) + 101 * k).shuffle(items)
        chunks, cur, size = [], [], 0
        for it in items:
            if cur and size + len(it[1]) > LIMIT_CHARS: chunks.append(cur); cur, size = [], 0
            cur.append(it); size += len(it[1])
        if cur: chunks.append(cur)
        labels = {}
        for n, chunk in enumerate(chunks):
            ctx = BlindCodingContext(coding, [t for _, t in chunk])
            answer = coder.chat(ctx.system(), ctx.user(), svc.temperature, ctx.responseFormat(), purpose="coding")
            codes = svc._codes(coder, answer)
            labels.update({r: (codes.get(str(i)) if codes.get(str(i)) in spec["labels"] else None) for i, (r, _) in enumerate(chunk)})
            print(f"{key} pass {k + 1} chunk {n + 1}/{len(chunks)} ({len(chunk)} cards) {time.time() - started:.0f}s", flush=True)
        passes.append(labels)
    final = {}
    for r, _ in base:
        votes = [p.get(r) for p in passes if p.get(r)]
        if not votes: final[r] = None; continue
        cnt = collections.Counter(votes); top = cnt.most_common(1)[0][1]
        final[r] = passes[0].get(r) if list(cnt.values()).count(top) > 1 and passes[0].get(r) in cnt else cnt.most_common(1)[0][0]
    byGroup = {g: dict(collections.Counter(v for r, v in final.items() if truth[r] == g)) for g in sorted(set(truth.values()))}
    agree = sum(1 for r, _ in base if len(set(p.get(r) for p in passes)) == 1)
    out[key] = {"byGroup": byGroup, "final": final, "truth": truth, "passes": passes, "unanimous": agree, "n": len(base)}
    json.dump(out, open(outPath, "w"), indent=1)
    print(f"== {key} '{spec['name']}': {byGroup}  unanimous {agree}/{len(base)}  {time.time() - started:.0f}s", flush=True)
print("done")
