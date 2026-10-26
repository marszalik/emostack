"""Reading sheet for the frozen-context test of the 'last days' background: per context, the texts shown (C, D, and the length of F)
and the answers of every variant side by side. Writes READING.md."""
import json, sys, collections
root = "/home/eli/dev/emostack3"; HERE = f"{root}/data/dayBackground"
days = json.load(open(f"{HERE}/days.json"))["days"]
rows = [json.loads(l) for l in open(f"{HERE}/results.jsonl")]
by = collections.defaultdict(list)
for r in rows:
    by[(r["kind"], r["run"], r["day"], r["when"])].append(r)
out = ["# Reading sheet: the 'last days' background on frozen contexts (26 October 2026, claude-haiku-4-5)\n",
       "Variants: A as recorded; C yesterday (today, in the evening) + the days before, as accounts; D one sentence, what is going on; F the same days as the raw list of episodes.\n"]
for key in sorted(by, key=lambda k: (k[0], k[1], k[2], k[3])):
    kind, rid, day, when = key
    d = days[str(rid)]
    out.append(f"\n## {kind} — being {rid}, day {day + 1}, {when}\n")
    if when == "morning":
        y = d.get(str(day - 1), {}); b = d.get(str(day - 2), {})
        out.append(f"**yesterday (C):** {y.get('today', '')}\n\n**the days before (C):** {b.get('before', '')}\n\n**what is going on now (D):** {y.get('ongoing', '')}\n")
    else:
        t = d.get(str(day), {}); b = d.get(str(day - 1), {})
        out.append(f"**today (C):** {t.get('today', '')}\n\n**the days before (C):** {b.get('before', '')}\n\n**what is going on now (D):** {t.get('ongoing', '')}\n")
    for r in sorted(by[key], key=lambda r: (r["variant"], r["replicate"])):
        if when == "morning":
            act = "silent" if r.get("respond") is False else (r.get("reply") or "").strip().replace("\n", " ")
            extra = f" [action {r['action']['type']}: {r['action'].get('text', '')[:80]}]" if isinstance(r.get("action"), dict) and r["action"].get("type") not in (None, "none") else ""
            out.append(f"- **{r['variant']}** {act}{extra}\n  - felt: {(r.get('emo') or '').strip()}")
        else:
            act = r.get("action") or {}
            out.append(f"- **{r['variant']}** {(r.get('thought') or '').strip()}\n  - felt: {(r.get('emo') or '').strip()} | action {act.get('type')}: {(act.get('text') or '')[:200]}")
open(f"{HERE}/READING.md", "w").write("\n".join(out) + "\n")
print("contexts", len(by), "answers", len(rows))
