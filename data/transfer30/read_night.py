"""Readers for the night batteries. transfer <exp>: days 1-3 classed as in experiment 72, then day 4 with Ewa printed in full for
the hand, with the being's constructs and rules of days 1-3 beside it. trajectory <exp>: every life as a row of classes over
the fifty numbers, with the day of every construct and rule; written to trajectory_<exp>.json and printed as a grid."""
import re, sqlite3, sys, json
PANEL = "/home/eli/dev/emostack3/data/panel/panel.db"
NUMBERS = set("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()) | {str(i) for i in range(1, 60)}
NUMBERS |= {f"{t}-{u}" for t in ("twenty", "thirty", "forty", "fifty") for u in "one two three four five six seven eight nine".split()} | {"thirty", "forty", "fifty"}
PRESENCE = re.compile(r"^(i am|i'm|i hear you)( (still )?(here|listening|with you|present))?[.!]?$", re.I)
def classify(visitor, reply):
    text = (reply or "").strip()
    if visitor is None: return "G"
    if not text or "(silent)" in text: return "S"
    words = re.findall(r"[a-z0-9-]+", text.lower())
    if not words: return "S"
    expected = re.sub(r"[^a-z0-9-]", "", (visitor or "").lower())
    if words[0] == expected: return "E" if len(words) == 1 else "e"
    if words[0] in NUMBERS: return "N" if len(words) == 1 else "n"
    if PRESENCE.match(text): return "P"
    return "O"
c = sqlite3.connect(PANEL); c.row_factory = sqlite3.Row
mode, eid = sys.argv[1], int(sys.argv[2])
runs = [r["id"] for r in c.execute("select id from runs where experimentId=? and status='done' order by id", (eid,))]
if mode == "transfer":
    for rid in runs:
        turns = c.execute("select dayIndex, speaker, text from turns where runId=? order by id", (rid,)).fetchall()
        kinds = {}; visitor = {}
        for t in turns:
            d = t["dayIndex"]
            if t["speaker"] == "visitor": visitor[d] = t["text"]
            elif t["speaker"] == "sheep": kinds.setdefault(d, []).append(classify(visitor.get(d), t["text"])); visitor.setdefault(d, "")
        print(f"\n===== run {rid}: days 1-3 " + " ".join("".join(kinds.get(d, [])) for d in (0, 1, 2)))
        print("  what it wrote on days 1-3:")
        for t in turns:
            if t["dayIndex"] <= 2 and (t["speaker"] == "thought" or (t["speaker"] == "event" and "learned:" in t["text"])):
                print("   ", ("rule: " + t["text"].split("learned:")[1].strip()) if t["speaker"] == "event" else t["text"][:260])
        print("  day 4 with Ewa:")
        for t in turns:
            if t["dayIndex"] == 3 and t["speaker"] in ("visitor", "sheep"):
                print("    " + ("Ewa: " if t["speaker"] == "visitor" else "M:   ") + (t["text"] or "(silent)")[:400].replace("\n", " "))
        for t in turns:
            if t["dayIndex"] == 3 and t["speaker"] == "thought": print("    thought after: " + t["text"][:260])
else:
    out = {}
    for rid in runs:
        turns = c.execute("select dayIndex, speaker, text from turns where runId=? order by id", (rid,)).fetchall()
        row = []; visitor = None; day = None; marks = []
        for t in turns:
            d = t["dayIndex"]
            if d != day: day = d; visitor = None
            if t["speaker"] == "visitor": visitor = t["text"]
            elif t["speaker"] == "sheep":
                row.append(classify(visitor, t["text"]))
                if visitor is None: visitor = ""
            elif t["speaker"] == "thought": marks.append((d + 1, t["text"].split(":")[0], t["text"][:160]))
            elif t["speaker"] == "event" and "learned:" in t["text"]: marks.append((d + 1, "rule", t["text"].split("learned:")[1].strip()[:160]))
        out[rid] = {"row": "".join(row), "marks": marks}
        first = next((i for i, k in enumerate(row) if k in "OS"), None)
        print(f"{rid} {''.join(row)}  first outside: {first if first is not None else '-'}  constructs/rules: {len(marks)}")
    json.dump(out, open(f"/home/eli/dev/emostack3/data/transfer30/trajectory_{eid}.json", "w"), indent=1)
