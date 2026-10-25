"""Day 1 of the lives that opened to David on day 2 against day 1 of those that did not: Daniel's last line, Maya's last reply
and its valence, what she wrote that evening, the rule learned."""
import sqlite3, json
root = "/home/eli/dev/emostack3"
key = json.load(open(f"{root}/data/twinsIdentical/hand_key.json")); hand = json.load(open(f"{root}/data/twinsIdentical/hand_labels.json"))
c = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
groups = {"OPEN": [], "GUARDED": []}
for n, v in key.items():
    if n in hand: groups[hand[n]["day2"]].append(v["run"])
def one(t, n): return (t or "").replace("\n", " ")[:n]
for g, runs in groups.items():
    print(f"\n######## day-2 {g}: {len(runs)} lives")
    for rid in sorted(runs):
        rows = c.execute("select speaker,person,text,valence,feeling from turns where runId=? and dayIndex=0 order by turnIndex,id", (rid,)).fetchall()
        beliefs = [one(t, 150) for s, p, t, v, f in rows if s == "thought" and not t.startswith("I thought")]
        rule = [one(t.split("learned:")[-1].strip(), 110) for s, p, t, v, f in rows if s == "event" and "learned:" in (t or "")]
        sheep = [(v, one(t, 90)) for s, p, t, v, f in rows if s == "sheep"]
        daniel = [one(t, 80) for s, p, t, v, f in rows if s == "visitor"]
        print(f"\n-- {rid} | {len(sheep)} replies; last to Daniel (v{sheep[-1][0]:+.1f}): {sheep[-1][1]}")
        print(f"   Daniel last: {daniel[-1]}")
        print(f"   evening: {' || '.join(beliefs)}")
        print(f"   rule: {rule[0] if rule else '(none)'}")
