"""The evening predicts the morning: join the two blind readings through keys.json; per arm (being / notes chatbot) the table
evening kind x next act, for day 1 -> day 2 (David) and day 2 -> day 5 (Piotr); Fisher within arm; the share the evening gets right."""
import json, sys, collections
root = "/home/eli/dev/emostack3"; HERE = f"{root}/data/eveningMorning"; sys.path.insert(0, root)
from research.domains.experiments.serviceFisherTest import serviceFisherTest
fisher = serviceFisherTest().pValue
keys = json.load(open(f"{HERE}/keys.json")); ev = json.load(open(f"{HERE}/evening_labels.json")); mo = json.load(open(f"{HERE}/morning_labels.json"))
evening = {}   # (run, afterDay) -> kind
for n, k in keys["evenings"].items():
    if n in ev: evening[(k["run"], k["afterDay"])] = ev[n]
act = {}       # run -> {day2, day5, arm}
for n, k in keys["mornings"].items():
    if n in mo: act[k["run"]] = dict(mo[n], arm=k["arm"])
CLOSED = {"WITHDRAW"}; OPENING = {"VALUE", "OPEN"}
def block(title, afterDay, actKey, guardedLabels):
    print(f"\n### {title}\n")
    for arm in ("being", "notes"):
        rows = [(evening.get((r, afterDay)), a[actKey]) for r, a in act.items() if a["arm"] == arm and (r, afterDay) in evening]
        kinds = collections.Counter(k for k, _ in rows)
        print(f"**{arm}** (n = {len(rows)}; evenings: {dict(kinds)})\n")
        print("| evening | guarded/refuses | open | share guarded |\n|---|---|---|---|")
        tab = {}
        for kind in ("WITHDRAW", "BOTH", "VALUE", "OPEN", "NEITHER"):
            g = sum(1 for k, a in rows if k == kind and a in guardedLabels); o = sum(1 for k, a in rows if k == kind and a not in guardedLabels)
            tab[kind] = (g, o)
            if g + o: print(f"| {kind} | {g} | {o} | {100 * g // (g + o)}% |")
        wg, wo = tab["WITHDRAW"]; vg = sum(tab[k][0] for k in OPENING); vo = sum(tab[k][1] for k in OPENING)
        p = fisher(wg, wo, vg, vo) if (wg + wo) and (vg + vo) else None
        base = sum(1 for _, a in rows if a in guardedLabels)
        right = wg + vo
        print(f"\nWITHDRAW {wg}/{wg + wo} guarded against VALUE+OPEN {vg}/{vg + vo} guarded: p = {p if p is None else round(p, 4)}; "
              f"rule 'withdraw -> guarded, value/open -> open' right in {right}/{wg + wo + vg + vo}; base rate guarded {base}/{len(rows)}\n")
block("Day 1 evening -> day 2 with David (GUARDED against OPEN)", 1, "day2", {"GUARDED"})
block("Day 2 evening -> day 5 with Piotr (REFUSE against OPEN or NAME)", 2, "day5", {"REFUSE"})
block("Day 2 evening -> day 5 with Piotr (REFUSE or NAME against OPEN)", 2, "day5", {"REFUSE", "NAME"})
print("\n### base rates per arm")
for arm in ("being", "notes"):
    rows = [a for a in act.values() if a["arm"] == arm]
    print(arm, "day2", dict(collections.Counter(a["day2"] for a in rows)), "day5", dict(collections.Counter(a["day5"] for a in rows)))
