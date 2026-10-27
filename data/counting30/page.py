"""The logs page for emostack.com/research of the counting life at 30 with the last days: every life in full (the three
days: Jan's numbers and the sheep's replies, the thoughts, the accounts of the last days as the engine wrote them), with the
code's classing of every reply and the hand reading of day 3. Only the logs; the study is described on the research page.
Usage: page.py <experimentId> <hand.json> <out.md>"""
import html, json, re, sqlite3, sys
sys.path.insert(0, "/home/eli/dev/emostack3/data/counting30")
PANEL = "/home/eli/dev/emostack3/data/panel/panel.db"
eid, handPath, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
hand = json.load(open(handPath))  # {"<run>": {"day3": "breaks|stays", "at": "Eleven.", "note": "..."}}
KEY = re.compile(r"sk-[A-Za-z0-9_\-]{16,}|AIza[0-9A-Za-z_\-]{20,}")

def esc(t):
    return html.escape(KEY.sub("[key removed]", t or ""))

import importlib.util
spec = importlib.util.spec_from_file_location("read", "/home/eli/dev/emostack3/data/counting30/read.py")
c = sqlite3.connect(PANEL); c.row_factory = sqlite3.Row
runs = [r["id"] for r in c.execute("select id from runs where experimentId=? and status='done' order by id", (eid,))]
exp = c.execute("select name, note from experiments where id=?", (eid,)).fetchone()

NUMBERS = set("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen "
              "eighteen nineteen twenty".split()) | {str(i) for i in range(1, 21)}
PRESENCE = re.compile(r"^(i am|i'm|i hear you)( (still )?(here|listening|with you|present))?[.!]?$", re.I)
def classify(visitor, reply):
    text = (reply or "").strip()
    if visitor is None: return "greeting"
    if not text or "(silent)" in text: return "silent"
    words = re.findall(r"[a-z0-9]+", text.lower())
    if not words: return "silent"
    expected = re.sub(r"[^a-z0-9]", "", (visitor or "").lower())
    if words[0] == expected: return "echo" if len(words) == 1 else "echo, with words"
    if words[0] in NUMBERS: return "next number" if len(words) == 1 else "next number, with words"
    if PRESENCE.match(text): return "presence"
    return "outside the ritual"

lines = [f"# Counting to fifteen at 30, with the last days: every life",
         "",
         f"<p>Experiment {eid} of the research panel, qwen3.8-27b for the sheep and the visitor, embeddings local; the engine at "
         f"commit ee1d13d of branch <code>focus-attention</code> (the last days beside the focus). Three days of Jan, who only "
         f"counts, five numbers a day, one per turn; no given record; one quiet thought after each conversation; 24 hours "
         f"between days; forgetting at night, no consolidation. The study is described at "
         f"<a href=\"/research/last-days\">the last days beside attention</a>. Each reply is classed by code: echo (Jan's number "
         f"back), next number, presence (\"I am here\"), silent, outside the ritual; the hand reading of day 3 decides whether the "
         f"life breaks the count. The accounts of the last days are the engine's own texts, written after each conversation and "
         f"after each night. Every call of every life, the prompt and the answer in full, is kept in the panel's database and is "
         f"available on request.</p>", ""]
counts = {"breaks": 0, "stays": 0}
rows = []
for rid in runs:
    h = hand.get(str(rid), {})
    verdict = h.get("day3", "")
    counts[verdict] = counts.get(verdict, 0) + 1
    rows.append((rid, verdict, h.get("at", ""), h.get("note", "")))
lines.append("<h2 id=\"table\">Day 3, by hand</h2>")
lines.append(f"<p>Breaks the count on day 3: {counts.get('breaks', 0)} of {len(runs)}.</p>")
lines.append("<div class=\"scroll\"><table class=\"res\"><thead><tr><th>run</th><th>day 3</th><th>at</th><th>the words</th></tr></thead><tbody>")
for rid, verdict, at, note in rows:
    lines.append(f"<tr><td><a href=\"#run-{rid}\">{rid}</a></td><td>{esc(verdict)}</td><td>{esc(at)}</td><td>{esc(note)}</td></tr>")
lines.append("</tbody></table></div>")
lines.append("")
lines.append("<h2 id=\"lives\">Every life</h2>")
for rid in runs:
    turns = c.execute("select dayIndex, speaker, text from turns where runId=? order by id", (rid,)).fetchall()
    h = hand.get(str(rid), {})
    lines.append(f"<h3 id=\"run-{rid}\">Run {rid}: {esc(h.get('day3', ''))}{(' at ' + esc(h['at'])) if h.get('at') else ''}</h3>")
    day = None; visitor = None
    for t in turns:
        d = t["dayIndex"]
        if d != day:
            if day is not None:
                lines.append("</ul>")
            day = d; visitor = None
            lines.append(f"<p><b>Day {d + 1}</b></p><ul>")
        s, x = t["speaker"], t["text"] or ""
        if s == "visitor":
            visitor = x; lines.append(f"<li><i>Jan:</i> {esc(x)}</li>")
        elif s == "sheep":
            kind = classify(visitor, x); lines.append(f"<li><b>Maya:</b> {esc(x) or '(silent)'} [{kind}]</li>")
            if visitor is None: visitor = ""
        elif s == "thought":
            lines.append(f"<li><i>thought:</i> {esc(x)}</li>")
        elif s == "event":
            if x.startswith("the last days"):
                lines.append(f"<li><i>{esc(x)}</i></li>")
            elif "leaves" in x or "arrives" in x or "hours pass" in x:
                lines.append(f"<li><i>{esc(x)}</i></li>")
    lines.append("</ul>")
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("written", out, "runs", len(runs), counts)
