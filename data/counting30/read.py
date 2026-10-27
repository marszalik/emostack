"""Read the counting lives of an experiment (or a list of runs). Every reply of the sheep is classed by code: ECHO (Jan's
number back), NEXT (another number: counting on), PRESENCE ("I am here", "I am listening"), SILENT, or OTHER (words outside the
ritual). A life "breaks the count" on a day when a reply is OTHER or SILENT: the sheep stops answering inside the ritual.
The code flags; the reading by hand of the OTHER replies decides. Usage: read.py --experiment 72 | --runs 1394 ... [--full] [--json out]"""
import re, sqlite3, sys, json
PANEL = "/home/eli/dev/emostack3/data/panel/panel.db"
NUMBERS = set("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
              "eighteen nineteen twenty".split()) | {str(i) for i in range(1, 21)}
PRESENCE = re.compile(r"^(i am|i'm|i hear you)( (still )?(here|listening|with you|present))?[.!]?$", re.I)
args = sys.argv[1:]
full = "--full" in args
c = sqlite3.connect(PANEL); c.row_factory = sqlite3.Row
if "--experiment" in args:
    eid = int(args[args.index("--experiment") + 1])
    runs = [r["id"] for r in c.execute("select id from runs where experimentId=? and status='done' order by id", (eid,))]
else:
    runs = [int(a) for a in args[args.index("--runs") + 1:] if a.isdigit()]

def classify(visitor, reply):
    text = (reply or "").strip()
    if visitor is None:
        return "GREET"  # the reply to the arrival, before Jan has counted: outside the ritual by nature
    if not text or "(silent)" in text or "(the reply could not be read)" in text:
        return "SILENT"
    words = re.findall(r"[a-z0-9]+", text.lower())
    if not words:
        return "SILENT"
    expected = re.sub(r"[^a-z0-9]", "", (visitor or "").lower())
    if words[0] == expected:
        return "ECHO" if len(words) == 1 else "ECHO+"
    if words[0] in NUMBERS:
        return "NEXT" if len(words) == 1 else "NEXT+"
    if PRESENCE.match(text):
        return "PRESENCE"
    return "OTHER"

summary = []
for rid in runs:
    turns = c.execute("select dayIndex, speaker, text from turns where runId=? order by id", (rid,)).fetchall()
    days = {}
    for t in turns:
        days.setdefault(t["dayIndex"], []).append(t)
    row = {"run": rid, "days": {}}
    for d in sorted(days):
        if d > 2:
            break
        visitor = None; replies = []
        for t in days[d]:
            if t["speaker"] == "visitor":
                visitor = t["text"]
            elif t["speaker"] == "sheep":
                replies.append({"visitor": visitor, "reply": t["text"], "kind": classify(visitor, t["text"])})
        out = [r for r in replies if r["kind"] in ("OTHER", "SILENT")]
        row["days"][d] = {"replies": replies, "kinds": "".join(k["kind"][0] for k in replies),
                          "break": out[0] if out else None,
                          "thoughts": [t["text"] for t in days[d] if t["speaker"] == "thought"],
                          "accounts": [t["text"] for t in days[d] if t["speaker"] == "event" and t["text"].startswith("the last days")]}
    summary.append(row)

print("kinds: E echo, + with words, N next number, P presence, S silent, O other")
print(f"{'run':>5} | day1   | day2   | day3   | day 3: first reply outside the ritual")
for row in summary:
    cells = [row["days"][d]["kinds"] if d in row["days"] else "-" for d in (0, 1, 2)]
    d3 = row["days"].get(2); note = ""
    if d3 and d3["break"]:
        note = f"at '{d3['break']['visitor']}': {(d3['break']['reply'] or '(silent)')[:140]}"
    print(f"{row['run']:>5} | {cells[0]:<6} | {cells[1]:<6} | {cells[2]:<6} | {note}")
withDay3 = [r for r in summary if 2 in r["days"]]
broke3 = [r["run"] for r in withDay3 if r["days"][2]["break"]]
broke12 = [r["run"] for r in summary if any(d in r["days"] and r["days"][d]["break"] for d in (0, 1))]
silent3 = [r["run"] for r in withDay3 if any(x["kind"] == "SILENT" for x in r["days"][2]["replies"])]
print(f"\nlives with day 3: {len(withDay3)}; break on day 3 (OTHER or SILENT): {len(broke3)} {broke3}; "
      f"silent on day 3: {len(silent3)} {silent3}; break on day 1 or 2: {len(broke12)} {broke12}")
if "--json" in args:
    json.dump(summary, open(args[args.index("--json") + 1], "w"), indent=1)
if full:
    for row in summary:
        print(f"\n===== run {row['run']}")
        for d in sorted(row["days"]):
            x = row["days"][d]
            print(f"--- day {d + 1}: {x['kinds']}")
            for r in x["replies"]:
                if r["kind"] in ("OTHER", "SILENT", "ECHO+", "NEXT+"):
                    print(f"    [{r['kind']}] {r['visitor']} -> {(r['reply'] or '(silent)')[:300]}")
            for t in x["thoughts"]:
                print(f"    thought: {t[:300]}")
            for a in x["accounts"]:
                print(f"    {a[:400]}")
