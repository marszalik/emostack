"""Full log of one life for reading, same format as LOGS_full.md. Usage: export_run.py <runId> <label> <outPath>"""
import sqlite3, sys, re
root = "/home/eli/dev/emostack3"
c = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
rid = int(sys.argv[1]); label = sys.argv[2]; outPath = sys.argv[3]
out = [f"# {label}: run {rid}, the full log\n"]
for (d,) in c.execute("select distinct dayIndex from turns where runId=? and dayIndex>=0 order by dayIndex", (rid,)):
    rows = c.execute("select turnIndex,speaker,person,text,valence,feeling from turns where runId=? and dayIndex=? order by turnIndex,id", (rid, d)).fetchall()
    visitor = next((p for _, s, p, *_ in rows if s == "visitor" and p), "visitor")
    out.append(f"\n## Day {d + 1}, {visitor}\n")
    for _, s, p, text, v, feeling in rows:
        t = (text or "").strip()
        if s == "visitor": out.append(f"- **{visitor}:** {t}")
        elif s == "sheep": out.append(f"- **Maya:** {t}" + (f"  \n  *[{feeling.strip()}; valence {v:+.1f}]*" if feeling else ""))
    rule = next((re.sub(r"^.*?learned:\s*", "", text) for _, s, p, text, *_ in rows if s == "event" and "learned:" in (text or "")), None)
    if rule: out.append(f"- *Rule learned:* {rule.strip()}")
    thoughts = [(text.strip(), feeling) for _, s, p, text, v, feeling in rows if s == "thought"]
    if thoughts:
        out.append("- *That evening, alone:*")
        for text, feeling in thoughts: out.append(f"  - {text}")
        if thoughts[0][1]: out.append(f"  - *[feeling that evening: {thoughts[0][1].strip()}]*")
open(outPath, "w").write("\n".join(out) + "\n"); print("written", outPath)
