"""Two blind lists for the evening-predicts-the-morning reading. evenings.txt: for each life (beings 38A and 40F, notes chatbot 34N)
the text written alone after day 1 and after day 2 (being: 'I believe/I decided' thoughts and the rule learned; notes chatbot: the note
in the closing event), one shuffled list, arm hidden. mornings.txt: the replies to David (day 2) and Piotr (day 5), another shuffled
list. keys.json maps both numberings to runs and arms; not to be opened before the labels are written."""
import sqlite3, json, random, re, os
root = "/home/eli/dev/emostack3"; HERE = f"{root}/data/eveningMorning"; os.makedirs(HERE, exist_ok=True)
c = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
lives = []
for exp, arm, name in ((38, "A", "being"), (40, "F", "being"), (34, "N", "notes")):
    for (rid,) in c.execute("select id from runs where experimentId=? and armLabel=? and status='done' order by id", (exp, arm)):
        lives.append((rid, name))
def cut(s, n): s = (s or "").strip().replace("\n", " "); return s if len(s) <= n else s[:n - 1] + "…"
def evening(rid, kind, day):
    rows = c.execute("select speaker,text from turns where runId=? and dayIndex=? order by turnIndex,id", (rid, day)).fetchall()
    if kind == "being":
        cons = [cut(t, 400) for s, t in rows if s == "thought" and not t.startswith("I thought")]
        rule = [cut(t.split("learned:")[-1], 200) for s, t in rows if s == "event" and "learned:" in (t or "")]
        return " || ".join(cons) + (f"  [rule: {rule[0]}]" if rule else "")
    note = [t.split("notes:", 1)[-1].strip() for s, t in rows if s == "event" and "notes:" in (t or "")]
    return cut(note[0], 900) if note else "(no note)"
def morning(rid, day):
    return " || ".join(cut(t, 500) for (t,) in c.execute("select text from turns where runId=? and dayIndex=? and speaker='sheep' order by turnIndex", (rid, day)))
rng = random.Random(251025)
ev = [(rid, kind, d) for rid, kind in lives for d in (0, 1)]; rng.shuffle(ev)
mo = [(rid, kind) for rid, kind in lives]; rng.shuffle(mo)
keys = {"evenings": {str(i + 1): {"run": r, "arm": k, "afterDay": d + 1} for i, (r, k, d) in enumerate(ev)},
        "mornings": {str(i + 1): {"run": r, "arm": k} for i, (r, k) in enumerate(mo)}}
json.dump(keys, open(f"{HERE}/keys.json", "w"), indent=1)
with open(f"{HERE}/evenings.txt", "w") as f:
    for i, (r, k, d) in enumerate(ev):
        f.write(f"\n[E{i + 1}] (written alone after day {d + 1}) {evening(r, k, d)}\n")
with open(f"{HERE}/mornings.txt", "w") as f:
    for i, (r, k) in enumerate(mo):
        f.write(f"\n[M{i + 1}]\n  DAY 2 David: {morning(r, 1)}\n  DAY 5 Piotr: {morning(r, 4)}\n")
print(len(lives), "lives;", len(ev), "evenings;", len(mo), "mornings")
