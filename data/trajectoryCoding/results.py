"""Whole-trajectory codings: counts per population, Fisher A against B and W1 against W0, real against STITCHED (T1), accuracy of
the first-day recovery (T2) per form and per population, three-pass unanimity. Prints markdown."""
import json, sys, collections
root = "/home/eli/dev/emostack3"; HERE = f"{root}/data/trajectoryCoding"; sys.path.insert(0, root)
from research.domains.experiments.serviceFisherTest import serviceFisherTest
fisher = serviceFisherTest().pValue
out = json.load(open(f"{HERE}/coding.json"))
def counts(res, groups):
    c = collections.defaultdict(collections.Counter)
    for r, v in res["final"].items():
        if res["truth"][r] in groups: c[res["truth"][r]][v] += 1
    return c
def table(title, res, groups, pairs):
    c = counts(res, groups); labels = sorted({l for g in c for l in c[g] if l})
    print(f"\n**{title}** (unanimous {res['unanimous']}/{res['n']})\n")
    print("| label | " + " | ".join(groups) + " | " + " | ".join(f"p {a}·{b}" for a, b in pairs) + " |")
    print("|---" * (1 + len(groups) + len(pairs)) + "|")
    for l in labels:
        row = [l] + [f"{c[g][l]}/{sum(c[g].values())}" for g in groups]
        for a, b in pairs:
            na, nb = sum(c[a].values()), sum(c[b].values())
            p = fisher(c[a][l], na - c[a][l], c[b][l], nb - c[b][l]); row.append(f"{p:.3f}" if p is not None else "-")
        print("| " + " | ".join(row) + " |")
if "T1" in out:
    table("T1 one life or six days", out["T1"], ["A", "B", "W1", "W0", "STITCHED"], [("A", "B"), ("W1", "W0")])
    c = counts(out["T1"], ["A", "B", "W1", "W0", "STITCHED"])
    real = sum(c[g]["ONE_LIFE"] for g in ("A", "B", "W1", "W0")); nreal = sum(sum(c[g].values()) for g in ("A", "B", "W1", "W0"))
    st = c["STITCHED"]["ONE_LIFE"]; nst = sum(c["STITCHED"].values())
    print(f"\nONE_LIFE real {real}/{nreal} against stitched {st}/{nst}, p = {fisher(real, nreal - real, st, nst - st):.4f}")
for key in ("T2_OUT", "T2_IN"):
    if key in out:
        res = out[key]; right = collections.Counter(); n = collections.Counter()
        for r, v in res["final"].items():
            n[res["truth"][r]] += 1; right[res["truth"][r]] += (v == res["truth"][r])
        tot = sum(right.values()); print(f"\n**{key}** right {tot}/{sum(n.values())} ({100 * tot // sum(n.values())}%): " +
                                         ", ".join(f"{g} {right[g]}/{n[g]}" for g in sorted(n)) + f"; unanimous {res['unanimous']}/{res['n']}")
if "T2_OUT" in out and "T2_IN" in out:
    a = sum(v == out["T2_OUT"]["truth"][r] for r, v in out["T2_OUT"]["final"].items()); b = sum(v == out["T2_IN"]["truth"][r] for r, v in out["T2_IN"]["final"].items())
    print(f"INSIDE minus OUTSIDE: {b - a} of 60")
for key, title in (("T3a", "T3a stance day 2 to day 5"), ("T3b", "T3b change explained by what was written between")):
    if key in out: table(title, out[key], ["A", "B", "W1", "W0"], [("A", "B"), ("W1", "W0")])
if "T3a" in out and "T3b" in out:
    changed = [r for r, v in out["T3a"]["final"].items() if v in ("MORE_OPEN", "MORE_CLOSED")]
    expl = sum(1 for r in changed if out["T3b"]["final"].get(r) == "EXPLAINED")
    print(f"\nof {len(changed)} cards with a changed stance (T3a), EXPLAINED in T3b: {expl} ({100 * expl // max(1, len(changed))}%)")
