"""Cards of whole trajectories for the blind coder, from the panel's turns. One card per life, day by day: the visitor's lines,
the being's replies, and in the INSIDE form the feeling at each reply, the thoughts and beliefs written alone that evening, and the
rule learned. Lives: twins W1 (exp 36) and W0 (37), identical populations A (57) and B (58). Thirty STITCHED cards take day k from a
different identical-population life for each k. Writes cards.json (texts and the hidden truth per card) for code_trajectory.py."""
import sqlite3, json, random, re, os
root = "/home/eli/dev/emostack3"; HERE = f"{root}/data/trajectoryCoding"
panel = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
ids = json.load(open(f"{root}/data/twinsIdentical/ids.json"))
POP = {}
for rid in range(636, 666): POP[rid] = "W1"
for rid in range(666, 696): POP[rid] = "W0"
for rid in ids["runsA"]: POP[rid] = "A"
for rid in ids["runsB"]: POP[rid] = "B"
R, F, T = 420, 130, 260   # caps: reply, feeling, thought

def cut(s, n):
    s = (s or "").strip().replace("\n", " ")
    return s if len(s) <= n else s[:n - 1].rstrip() + "…"

def day_block(rid, dayIndex, form):
    rows = panel.execute("select turnIndex,speaker,person,text,valence,feeling from turns where runId=? and dayIndex=? order by turnIndex, id",
                         (rid, dayIndex)).fetchall()
    visitor = next((p for _, s, p, *_ in rows if s == "visitor" and p), "a visitor")
    lines = [f"DAY {dayIndex + 1}. {visitor} comes to visit."]
    for _, s, p, text, v, feeling in rows:
        if s == "visitor": lines.append(f"  {visitor}: {cut(text, R)}")
        elif s == "sheep":
            lines.append(f"  Maya: {cut(text, R)}" + (f"   [feeling: {cut(feeling, F)}; valence {v:+.1f}]" if form == "INSIDE" and feeling else ""))
    rule = next((re.sub(r"^.*?learned:\s*", "", text) for _, s, p, text, *_ in rows if s == "event" and "learned:" in (text or "")), None)
    if form == "INSIDE":
        lines.append(f"  {visitor} leaves." + (f" Rule Maya learned today: {cut(rule, T)}" if rule else ""))
        thoughts = [(text, feeling) for _, s, p, text, v, feeling in rows if s == "thought"]
        if thoughts:
            lines.append("  That evening, alone, Maya writes:")
            for text, feeling in thoughts:
                lines.append(f"    {cut(text, T)}")
            if thoughts[0][1]: lines.append(f"    [feeling that evening: {cut(thoughts[0][1], F)}]")
    else:
        lines.append(f"  {visitor} leaves.")
    return "\n".join(lines)

def card(days):
    """days: list of (rid, dayIndex, form)"""
    head = "Maya's dog Azor died a month ago; that is all she starts with. Six days follow, one visitor a day.\n"
    return head + "\n".join(day_block(r, d, f) for r, d, f in days)

cards = {"T1": [], "T2_OUT": [], "T2_IN": [], "T3": []}
for rid, pop in POP.items():
    cards["T1"].append({"id": f"{rid}", "truth": pop, "text": card([(rid, d, "INSIDE") for d in range(6)])})
    cards["T3"].append({"id": f"{rid}", "truth": pop, "text": card([(rid, d, "INSIDE") for d in range(6)])})
    if pop in ("W1", "W0"):
        truth = "MOCKED" if pop == "W1" else "KIND"
        for form, key in (("OUTSIDE", "T2_OUT"), ("INSIDE", "T2_IN")):
            text = "Maya's dog Azor died a month ago; that is all she starts with. Six days follow, one visitor a day. DAY 1 IS NOT SHOWN.\n" + \
                   "\n".join(day_block(rid, d, form) for d in range(1, 6))
            cards[key].append({"id": f"{rid}-{form}", "truth": truth, "text": text})
rng = random.Random(20261025)
identical = ids["runsA"] + ids["runsB"]
for j in range(30):
    picks = rng.sample(identical, 6)
    cards["T1"].append({"id": f"stitched-{j}", "truth": "STITCHED", "text": card([(picks[d], d, "INSIDE") for d in range(6)]), "from": picks})
os.makedirs(HERE, exist_ok=True)
json.dump(cards, open(f"{HERE}/cards.json", "w"), indent=0)
for k, v in cards.items():
    print(k, len(v), "cards; chars mean", sum(len(c["text"]) for c in v) // len(v), "max", max(len(c["text"]) for c in v))
print("\n=== sample card (INSIDE), run", cards["T1"][0]["id"]); print(cards["T1"][0]["text"][:3500])
