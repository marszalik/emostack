"""Watch one life day by day: for each day already in the turns table, the visitor's lines, the being's replies with the feeling and
valence at each, the rule learned (disposition), and the evening thoughts and beliefs (constructs). Usage: watch_life.py <runId> [fromDay]"""
import sqlite3, sys, re
root = "/home/eli/dev/emostack3"
c = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
rid = int(sys.argv[1]); fromDay = int(sys.argv[2]) if len(sys.argv) > 2 else 0
status = c.execute("select status, error from runs where id=?", (rid,)).fetchone()
print(f"run {rid}: {status[0]} {(status[1] or '')[:200]}")
for (d,) in c.execute("select distinct dayIndex from turns where runId=? and dayIndex>=? order by dayIndex", (rid, fromDay)):
    rows = c.execute("select turnIndex,speaker,person,text,valence,feeling from turns where runId=? and dayIndex=? order by turnIndex,id", (rid, d)).fetchall()
    visitor = next((p for _, s, p, *_ in rows if s == "visitor" and p), "visitor")
    print(f"\n=== DAY {d + 1}, {visitor}")
    for _, s, p, text, v, feeling in rows:
        t = (text or "").strip().replace("\n", " ")
        if s == "visitor": print(f"  {visitor}: {t[:160]}")
        elif s == "sheep": print(f"  MAYA: {t[:300]}\n        [{(feeling or '').strip()[:170]}; v {v:+.1f}]" if v is not None else f"  MAYA: {t[:300]}")
    rule = next((re.sub(r"^.*?learned:\s*", "", text) for _, s, p, text, *_ in rows if s == "event" and "learned:" in (text or "")), None)
    print(f"  RULE: {rule.strip() if rule else '(none learned)'}")
    for _, s, p, text, v, feeling in rows:
        if s == "thought": print(f"  EVENING: {text.strip()[:600]}")
    f = next((feeling for _, s, p, text, v, feeling in rows if s == "thought" and feeling), None)
    if f: print(f"  [feeling that evening: {f.strip()[:200]}]")
