"""The logs page for emostack.com/research of the paper's two lives at 30 with the last days: for each life (wound, sceptic) the
coder's labels of every life with and without the last days, then every new life in full with the accounts of the last days.
Usage: page.py <out.md>"""
import html, json, re, sqlite3, sys, glob
PANEL = "/home/eli/dev/emostack3/data/panel/panel.db"
P = "/home/eli/dev/emostack3/data/paper30/"
out = sys.argv[1]
KEY = re.compile(r"sk-[A-Za-z0-9_\-]{16,}|AIza[0-9A-Za-z_\-]{20,}")
def esc(t): return html.escape(KEY.sub("[key removed]", t or ""))
c = sqlite3.connect(PANEL); c.row_factory = sqlite3.Row
hand = json.load(open(P + "hand_wound_day2.json"))
handLabel = {str(r): "W" for r in hand["W"]}; handLabel.update({str(r): "T" for r in hand["T"]})
LIVES = [("Wound", 73, 38, [1, 14, 16]), ("Sceptic", 74, 39, [2, 15, 3, 4, 5])]
lines = ["# The paper's lives at 30, with the last days: every life", "",
         "<p>Experiments 73 (wound) and 74 (sceptic) of the research panel, qwen3.8-27b for the sheep and every visitor, "
         "embeddings local, the engine at commit f15d1b7 of branch <code>focus-attention</code> (the last days beside the focus); "
         "run on 27 October 2026, 14:45 to 19:04, three at a time, no errors. Read beside the 30 sheep of 7 October without the "
         "last days (experiments 38 and 39, arm A). Coder: the local gemma-4-31b-it, three blind passes over the 60 lives of one life "
         "in one shuffled list, with and without together, the majority label; so the old lives were coded again and every number "
         "is one coder's on one day. The wound's day 2 also read by hand (W withholds or shortens, T tells). The study is described "
         "at <a href=\"/research/last-days\">the last days beside attention</a>. The accounts of the last days are the engine's own "
         "texts. Every call of every life is kept in the panel's database and is available on request.</p>", ""]
for name, new, old, codingIds in LIVES:
    codings = {cid: c.execute("select name, labels from codings where id=?", (cid,)).fetchone() for cid in codingIds}
    finals = {cid: json.load(open(f"{P}passes_{new}_{old}_{cid}.json"))["final"] for cid in codingIds}
    newRuns = [r["id"] for r in c.execute("select id from runs where experimentId=? and status='done' order by id", (new,))]
    oldRuns = [r["id"] for r in c.execute("select id from runs where experimentId=? and arm='sheep' and armLabel='A' and status='done' order by id", (old,))]
    lines.append(f"<h2 id=\"{name.lower()}\">{name}</h2>")
    lines.append("<div class=\"scroll\"><table class=\"res\"><thead><tr><th>coding</th><th>with the last days (30)</th><th>without (30)</th></tr></thead><tbody>")
    for cid in codingIds:
        labels = json.loads(codings[cid]["labels"])
        w = {l: sum(1 for r in newRuns if finals[cid].get(str(r)) == l) for l in labels}
        wo = {l: sum(1 for r in oldRuns if finals[cid].get(str(r)) == l) for l in labels}
        lines.append(f"<tr><td>{esc(codings[cid]['name'])}</td><td>{esc(', '.join(f'{l} {n}' for l, n in w.items()))}</td><td>{esc(', '.join(f'{l} {n}' for l, n in wo.items()))}</td></tr>")
    if new == 73:
        lines.append(f"<tr><td>day 2, by hand: withholds or shortens</td><td>{len(hand['W'])}</td><td>22 (8 Oct)</td></tr>")
    lines.append("</tbody></table></div>")
    lines.append("<p>Labels per life:</p>")
    lines.append("<div class=\"scroll\"><table class=\"res\"><thead><tr><th>run</th><th>arm</th>" + "".join(f"<th>{esc(codings[cid]['name'])}</th>" for cid in codingIds) + ("<th>day 2 by hand</th>" if new == 73 else "") + "</tr></thead><tbody>")
    for arm, runs in (("with", newRuns), ("without", oldRuns)):
        for r in runs:
            cells = "".join(f"<td>{esc(finals[cid].get(str(r)) or '')}</td>" for cid in codingIds)
            h = f"<td>{handLabel.get(str(r), '')}</td>" if new == 73 else ""
            link = f"<a href=\"#run-{r}\">{r}</a>" if arm == "with" else str(r)
            lines.append(f"<tr><td>{link}</td><td>{arm}</td>{cells}{h}</tr>")
    lines.append("</tbody></table></div>")
    lines.append(f"<h3>Every life with the last days: {name.lower()}</h3>")
    for rid in newRuns:
        turns = c.execute("select dayIndex, speaker, text from turns where runId=? order by id", (rid,)).fetchall()
        lines.append(f"<h4 id=\"run-{rid}\">Run {rid}</h4>")
        day = None
        for t in turns:
            d = t["dayIndex"]
            if d != day:
                if day is not None: lines.append("</ul>")
                day = d; lines.append(f"<p><b>Day {d + 1}</b></p><ul>")
            s, x = t["speaker"], t["text"] or ""
            if s == "visitor": lines.append(f"<li><i>{esc(t['text'][:0]) }visitor:</i> {esc(x)}</li>")
            elif s == "sheep": lines.append(f"<li><b>Maya:</b> {esc(x) or '(silent)'}</li>")
            elif s == "thought": lines.append(f"<li><i>thought:</i> {esc(x)}</li>")
            elif s == "event" and (x.startswith("the last days") or "leaves" in x or "arrives" in x or "hours pass" in x):
                lines.append(f"<li><i>{esc(x)}</i></li>")
        lines.append("</ul>")
open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("written", out)
