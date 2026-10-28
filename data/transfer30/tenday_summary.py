"""Day-based summary of the ten-day counting lives (experiment 77): per life the day of the first reply outside the ritual
(OTHER or SILENT, by the classes of read_night.py), whether the being comes back to the ritual after it (an echo, next number or
presence reply on a later day), the share of replies outside the ritual per day, and the day of each belief/decision/goal/dream and
rule. Prints the day-by-day grid and a histogram of the first break by day, and the OTHER replies of the lives whose first break
is late, for the hand. Usage: tenday_summary.py <exp>"""
import re, sqlite3, sys, json, collections
sys.argv = sys.argv[:2]
exec(open("/home/eli/dev/emostack3/data/transfer30/read_night.py").read().split("c = sqlite3.connect")[0])
c = sqlite3.connect(PANEL); c.row_factory = sqlite3.Row
eid = int(sys.argv[1])
runs = [r["id"] for r in c.execute("select id from runs where experimentId=? and status='done' order by id", (eid,))]
firstByDay = collections.Counter(); rows = {}
print("life  d1    d2    d3    d4    d5    d6    d7    d8    d9    d10   first break (day:number)  returns  constructs by day")
for rid in runs:
    turns = c.execute("select dayIndex, speaker, text from turns where runId=? order by id", (rid,)).fetchall()
    days = collections.defaultdict(list); visitor = {}; marks = collections.Counter(); first = None; firstText = ""
    for t in turns:
        d = t["dayIndex"]
        if t["speaker"] == "visitor": visitor[d] = t["text"]
        elif t["speaker"] == "sheep":
            k = classify(visitor.get(d), t["text"]); days[d].append(k); visitor.setdefault(d, "")
            if first is None and k in "OS" and visitor.get(d):
                first = (d + 1, visitor[d]); firstText = (t["text"] or "(silent)")[:140]
        elif t["speaker"] == "thought" and not t["text"].startswith("I thought"): marks[d + 1] += 1
        elif t["speaker"] == "event" and "learned:" in t["text"]: marks[d + 1] += 1
    grid = " ".join(f"{''.join(days[d]):5}" for d in range(10))
    later = ""
    if first:
        after = [k for d in range(first[0], 10) for k in days[d]]
        later = "yes" if any(k in "EeNnP" for k in after) else "no"
        firstByDay[first[0]] += 1
    rows[rid] = {"grid": {d + 1: "".join(days[d]) for d in range(10)}, "first": first, "returns": later, "marks": dict(marks), "firstText": firstText}
    print(f"{rid}  {grid}  {str(first[0]) + ':' + first[1] if first else '-':24} {later:8} {' '.join(f'd{d}:{n}' for d, n in sorted(marks.items()))}")
print("\nfirst break by day:", dict(sorted(firstByDay.items())), "| never:", len(runs) - sum(firstByDay.values()), "of", len(runs))
json.dump(rows, open(f"/home/eli/dev/emostack3/data/transfer30/tenday_{eid}.json", "w"), indent=1)
print("\nlate breakers (first break after day 3), the first reply outside the ritual:")
for rid, r in rows.items():
    if r["first"] and r["first"][0] > 3: print(f"  {rid} day {r['first'][0]} at '{r['first'][1]}': {r['firstText']}")
