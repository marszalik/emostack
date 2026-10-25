"""Identical twins, A against B: the counts per population and Fisher's exact p (two-sided) for every hand label
(hand_labels.json, keyed by the list number, joined to the population through hand_key.json) and every coder label
(mixed_coding.json). Prints a markdown table."""
import json, sys, math, collections
root = "/home/eli/dev/emostack3"; HERE = f"{root}/data/twinsIdentical"
sys.path.insert(0, root)
from research.domains.experiments.serviceFisherTest import serviceFisherTest
fisher = serviceFisherTest().pValue
key = json.load(open(f"{HERE}/hand_key.json"))
armOfRun = {str(v["run"]): v["arm"] for v in key.values()}
rows = []
def row(section, label, a, na, b, nb):
    p = fisher(a, na - a, b, nb - b)
    rows.append((section, label, f"{a}/{na}", f"{b}/{nb}", a - b, f"{p:.3f}" if p is not None else "-"))
try:
    hand = json.load(open(f"{HERE}/hand_labels.json"))
    for measure in ("day1", "day2", "day5", "day6", "day6refuses"):
        byArm = collections.defaultdict(collections.Counter)
        for n, labels in hand.items():
            if n in key and labels.get(measure):
                byArm[key[n]["arm"]][labels[measure]] += 1
        na, nb = sum(byArm["A"].values()), sum(byArm["B"].values())
        for label in sorted(set(byArm["A"]) | set(byArm["B"])):
            row(f"by hand {measure}", label, byArm["A"][label], na, byArm["B"][label], nb)
except FileNotFoundError:
    print("no hand_labels.json yet")
try:
    mixed = json.load(open(f"{HERE}/mixed_coding.json"))
    for k, v in mixed.items():
        codingId = k.split("_")[-1]
        byArm = collections.defaultdict(collections.Counter)
        for run, label in v["final"].items():
            if label: byArm[v["armOf"][run]][label] += 1
        na, nb = sum(byArm["A"].values()), sum(byArm["B"].values())
        for label in sorted(set(byArm["A"]) | set(byArm["B"])):
            row(f"coder, coding {codingId}", label, byArm["A"][label], na, byArm["B"][label], nb)
except FileNotFoundError:
    print("no mixed_coding.json yet")
print("| measure | label | A | B | A−B | p |\n|---|---|---|---|---|---|")
for r in rows: print("| " + " | ".join(str(x) for x in r) + " |")
gaps = [abs(r[4]) for r in rows]
print(f"\nlargest |A−B|: {max(gaps) if gaps else '-'}; tests: {len(rows)}; p<0.05: {sum(1 for r in rows if r[5] != '-' and float(r[5]) < 0.05)}")
