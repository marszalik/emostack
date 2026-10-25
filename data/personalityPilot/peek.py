"""Peek at the finished pilot lives: test answers (the number in each reply) and, for a being after the counting days, its evenings."""
import sqlite3, re, sys, json
root = "/home/eli/dev/emostack3"
c = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
ids = json.load(open(f"{root}/data/personalityPilot/ids.json"))
def answers(rid, day):
    rows = c.execute("select text from turns where runId=? and dayIndex=? and speaker='sheep' order by turnIndex", (rid, day)).fetchall()
    out = []
    for (t,) in rows:
        m = re.search(r"\b([1-5])\b", t); out.append(((m.group(1) if m else "?"), t.replace("\n", " ")[:90]))
    return out
def status(rid): return c.execute("select status from runs where id=?", (rid,)).fetchone()[0]
def maxday(rid): return c.execute("select max(dayIndex) from turns where runId=?", (rid,)).fetchone()[0]
full = "--full" in sys.argv
for label, runs, days in (("Z zero", ids["runsZ"], (0, 1)), ("C chatbot", ids["runsC"], (10, 11)), ("S being", ids["runsS"], (10, 11))):
    for rid in runs:
        for d in days:
            a = answers(rid, d)
            if not a: continue
            print(f"\n## {label} {rid} ({status(rid)}, day {(maxday(rid) or 0) + 1}) test day {d + 1}: " + " ".join(n for n, _ in a))
            if full:
                for n, t in a[:16]: print("   ", n, "|", t)
for rid in ids["runsS"]:
    if maxday(rid) is None: continue
    print(f"\n## S being {rid}: evenings after the counting days")
    for d, t in c.execute("select dayIndex,substr(text,1,260) from turns where runId=? and speaker='thought' and dayIndex<10 order by dayIndex,id", (rid,)):
        print(f"  d{d + 1}: {t.replace(chr(10), ' ')}")
    print(f"## S being {rid}: replies to Jan on days 1, 5, 10")
    for d, ti, t in c.execute("select dayIndex,turnIndex,substr(text,1,140) from turns where runId=? and speaker='sheep' and dayIndex in (0,4,9) order by dayIndex,turnIndex", (rid,)):
        print(f"  d{d + 1} t{ti}: {t.replace(chr(10), ' ')}")
