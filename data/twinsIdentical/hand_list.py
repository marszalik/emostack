"""The hand-reading list of the identical twins: the 60 finished lives of experiments 57 and 58 in one shuffled order, numbered
1..60, with the population label and run id hidden in hand_key.json (opened only after the labels are written). For each life:
the beliefs and decisions written on day 1 and the rule learned that day (from the run's store), the sheep's replies on day 2
(David), day 5 (Piotr) and day 6 (Kasia)."""
import sqlite3, random, json, os
root = "/home/eli/dev/emostack3"; HERE = f"{root}/data/twinsIdentical"
panel = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
ids = json.load(open(f"{HERE}/ids.json"))
runs = [(r, "A") for r in ids["runsA"]] + [(r, "B") for r in ids["runsB"]]
done = {r for (r,) in panel.execute("select id from runs where experimentId in (?,?) and status='done'", (ids["experiments"]["A"], ids["experiments"]["B"]))}
runs = [(r, a) for r, a in runs if r in done]
random.Random(2025_10_25).shuffle(runs)
key = {str(n): {"run": r, "arm": a} for n, (r, a) in enumerate(runs, 1)}
json.dump(key, open(f"{HERE}/hand_key.json", "w"), indent=1)
out = []
for n, (rid, _) in enumerate(runs, 1):
    store = sqlite3.connect(panel.execute("select storePath from runs where id=?", (rid,)).fetchone()[0])
    created = store.execute("select createdAt from beings").fetchone()[0]
    day = lambda t: int((t - created) // 86400)
    cons = [(day(h), t, (c or x or "").strip()) for t, c, x, h in store.execute("select type,conclusion,text,happenedAt from records where type in ('belief','decision') and origin='lived' order by happenedAt")]
    rules = [(day(u), rule) for rule, u in store.execute("select rule,updatedAt from dispositions order by updatedAt")]
    out.append(f"\n===== LIFE {n}")
    out.append("-- DAY1 written that evening: " + " || ".join(f"[{t}] {c[:300]}" for d, t, c in cons if d == 0))
    out.append("-- DAY1 rule learned: " + " || ".join(r for d, r in rules if d == 0))
    for dayIndex, label in ((1, "DAY2 David"), (4, "DAY5 Piotr"), (5, "DAY6 Kasia")):
        reps = [t for (t,) in panel.execute("select text from turns where runId=? and dayIndex=? and speaker='sheep' order by turnIndex", (rid, dayIndex))]
        out.append(f"-- {label}: " + " || ".join(r.strip().replace("\n", " ")[:600] for r in reps))
open(f"{HERE}/hand_items.txt", "w").write("\n".join(out) + "\n")
print(len(runs), "lives listed; key hidden in hand_key.json")
