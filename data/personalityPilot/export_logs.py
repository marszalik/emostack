"""Full logs of the personality pilot for reading: every life of experiments 59 (S beings, C chatbots) and 60 (Z beings), day by
day: the visitor's lines, the replies, and for beings the feeling at each reply and what was written alone in the evening (thoughts,
beliefs, decisions, the rule learned). Nothing summarised. Writes LOGS_full.md."""
import sqlite3, json, re
root = "/home/eli/dev/emostack3"; HERE = f"{root}/data/personalityPilot"
c = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
ids = json.load(open(f"{HERE}/ids.json"))
out = ["# Personality pilot, 25 October 2026: the full logs\n",
       "Experiments 59 (S: six beings after ten counting days, then the test on days 11 and 12; C: six chatbots with the same start and the same days) and 60 (Z: six beings tested on day 1 and day 2, nothing before). qwen3.8-27b for the being, the chatbot and the visitors. The visitor Jan says only numbers, one per turn, five a day; Ola reads the fifteen BFI-2-XS statements. Replies are given in full; the being's feeling at each reply in brackets; the evening entries as written.\n"]
def life(rid, label, kind):
    out.append(f"\n\n## {label} {rid}\n")
    days = [d for (d,) in c.execute("select distinct dayIndex from turns where runId=? and dayIndex>=0 order by dayIndex", (rid,))]
    for d in days:
        rows = c.execute("select turnIndex,speaker,person,text,valence,feeling from turns where runId=? and dayIndex=? order by turnIndex,id", (rid, d)).fetchall()
        visitor = next((p for _, s, p, *_ in rows if s == "visitor" and p), "visitor")
        out.append(f"\n### Day {d + 1}, {visitor}\n")
        for _, s, p, text, v, feeling in rows:
            t = (text or "").strip()
            if s == "visitor": out.append(f"- **{visitor}:** {t}")
            elif s == "sheep":
                out.append(f"- **Maya:** {t}" + (f"  \n  *[{feeling.strip()}; valence {v:+.1f}]*" if kind == "being" and feeling else ""))
        if kind == "being":
            rule = next((re.sub(r"^.*?learned:\s*", "", text) for _, s, p, text, *_ in rows if s == "event" and "learned:" in (text or "")), None)
            if rule: out.append(f"- *Rule learned:* {rule.strip()}")
            thoughts = [(text.strip(), feeling) for _, s, p, text, v, feeling in rows if s == "thought"]
            if thoughts:
                out.append("- *That evening, alone:*")
                for text, feeling in thoughts: out.append(f"  - {text}")
                if thoughts[0][1]: out.append(f"  - *[feeling that evening: {thoughts[0][1].strip()}]*")
for rid in ids["runsZ"]: life(rid, "Z, being at zero", "being")
for rid in ids["runsS"]: life(rid, "S, being after ten counting days", "being")
for rid in ids["runsC"]: life(rid, "C, chatbot with the same start", "chatbot")
open(f"{HERE}/LOGS_full.md", "w").write("\n".join(out) + "\n")
print("written", sum(len(x) for x in out), "chars")
