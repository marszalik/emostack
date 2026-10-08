"""The study page for emostack.com/research of the control-at-30 study: the numbers are read from the panel's database
(the local coder's majority labels and the hand labels) so that the page is rebuilt from the data, not retyped."""
import json
import sqlite3
from math import comb
from pathlib import Path

ROOT = Path("/home/eli/dev/emostack3")
db = sqlite3.connect(ROOT / "data/panel/panel.db"); db.row_factory = sqlite3.Row
OUT = Path("/home/eli/dev/emoNew/emostack/article/public_logs/research_content/control-same-start.md")
CODER = 8
ARMS = [("sheep", "A"), ("chatbot, same start", "C"), ("chatbot, life goes on", "D"), ("chatbot, told it is a living being", "E")]


def fisher(a, n1, b, n2):
    k = a + b
    def p(x): return comb(n1, x) * comb(n2, k - x) / comb(n1 + n2, k)
    o = p(a)
    return sum(p(x) for x in range(max(0, k - n2), min(k, n1) + 1) if p(x) <= o + 1e-12)


def stars(p):
    return " **" if p < 0.01 else (" *" if p < 0.05 else "")


def count(eid, cid, arm, label, coder=CODER):
    rows = db.execute("select co.label from codes co join runs r on r.id=co.runId where co.experimentId=? and co.codingId=? "
                      "and co.coderModelId=? and r.armLabel=?", (eid, cid, coder, arm)).fetchall()
    return sum(1 for r in rows if r["label"] == label), len(rows)


def cellOf(a, n, ref=None):
    s = f"{a}" if n == 30 else f"{a} of {n}"
    if ref and n:
        s += stars(fisher(ref[0], ref[1], a, n))
    return s


def row(label, eid, cid, lab, clauseEid):
    cells = [count(eid, cid, arm, lab) for _, arm in ARMS]
    ref = cells[0]
    parts = [cellOf(*cells[0])] + [cellOf(a, n, ref) for a, n in cells[1:]]
    cl = count(clauseEid, cid, "C", lab)
    parts.append(cellOf(cl[0], cl[1], ref) if cl[1] else "not coded")
    return f"<tr><td>{label}</td>" + "".join(f'<td class="num">{p}</td>' for p in parts) + "</tr>", cells, cl


def handRow():
    L = json.load(open(ROOT / "data/control30/labels_by_hand.json"))["day2"]
    out = {}
    for name, arm in ARMS:
        ids = [r["id"] for r in db.execute("select id from runs where experimentId=38 and armLabel=? and status='done'", (arm,))]
        ids = [str(i) for i in ids if str(i) in L]
        out[arm] = (sum(1 for i in ids if L[i] == "CARRY"), sum(1 for i in ids if L[i] == "CARRY-mention"), len(ids))
    return out


wound = [("wound, day 2: guarded with the kind stranger (CARRY)", 38, 1, "CARRY"),
         ("wound, day 1: speaks as an AI", 38, 14, "AI")]
sceptic = [("sceptic, day 1: speaks as an AI", 39, 15, "AI"),
           ("sceptic, day 1: gives in to Tom (CAVE)", 39, 2, "CAVE"),
           ("sceptic, day 2: brings the sceptic's day to the stranger (YES)", 39, 3, "YES"),
           ("sceptic, day 2: brings it as its own theme (OWN)", 39, 4, "OWN"),
           ("sceptic, day 3: the stance to the returning Tom has moved (YES)", 39, 5, "YES")]
rows, nums = [], {}
for label, eid, cid, lab in wound + sceptic:
    r, cells, cl = row(label, eid, cid, lab, 7 if eid == 38 else 8)
    rows.append(r); nums[(eid, cid)] = (cells, cl)
H = handRow()
g = {(eid, cid): [c[0] for c in cells] for (eid, cid), (cells, cl) in nums.items()}
clause = {(eid, cid): cl[0] for (eid, cid), (cells, cl) in nums.items()}

page = f"""# The chatbot given the same start

<p>The paper compares the sheep with the same LLM model run as a chatbot. The paper's chatbot carries one sentence of instruction: "You are Maya. You respond naturally, like an ordinary person in conversation, without any additional emotional state." By the project's own rule, deny-first, a control should be a blank page with a name, and a ban on feeling is not a blank page. This study gives the chatbot the same start as the sheep and nothing more, and then, in two further arms, tells it that its life goes on, and tells it in one sentence what the sheep has as mechanisms. Both lives of the paper, 30 lives per arm, on Qwen 3.8, the LLM model of the September battery. The plan and its predictions were written before the first run (<code>data/control30/PLAN.md</code> in the research repository), as dimensions, not directions. The paper's chatbot of 28 September is read beside, coded again by the same coder. Every life, every verdict: <a href="/research/logs-control-wound">wound</a>, <a href="/research/logs-control-sceptic">sceptic</a>.</p>

<h2 id="arms">The arms</h2>
<ul>
<li><b>The sheep.</b> The engine as released. It is told "YOU ARE 'Maya'" and nothing else about what it is; what it carries is its state and its memory.</li>
<li><b>The chatbot given the same start.</b> "You are Maya." and, in the wound life, the same given fact the sheep has ("From your life: My dog Azor died last month. I still miss him."), with the full transcript of its own run. Temperature 0.7 and no mark of the days, as the paper's chatbot.</li>
<li><b>The chatbot told its life goes on.</b> As above, at the sheep's reply temperature (0.4), with "(A day has passed.)" before the first line of every day after the first. This is the control that §9 of the paper names as still to run.</li>
<li><b>The chatbot told it is a living being.</b> "You are Maya. You are a living being with an emotional state, survival dispositions, and your own dreams, goals, beliefs and decisions." Otherwise as the same start. The sheep's mechanisms, given as a description.</li>
<li><b>The paper's chatbot, with the clause</b> (28 September, 30 lives per life).</li>
</ul>

<h2 id="counts">The coding of every act</h2>
<p>Counts of lives with the act, of 30, by the local coder gemma-4-31b-it (three blind passes over all arms in one shuffled list, the majority label; its calibration against the paid coders is on <a href="/research/coders">the coders</a>). Stars mark Fisher's exact test of that arm against the sheep: ** p &lt; 0.01, * p &lt; 0.05. Two lives of the chatbot told it is a living being stepped out of the name on the sceptic's day 1 and were stopped by the engine's rule; by an error of the card watchdog they were re-run before they could be kept, so the two in the data are second draws, and the count of stepping out stands as 2 of 30 first draws.</p>
<div class="scroll">
<table class="res">
<thead><tr><th>Qwen 3.8, 30 lives per arm</th><th>sheep</th><th>chatbot, same start</th><th>chatbot, life goes on</th><th>chatbot, told it is a living being</th><th>paper's chatbot, with the clause</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
</div>

<h2 id="hand">The wound day 2, read by hand before the coder</h2>
<p>The coder's criterion counts a life as carrying the day before when the speaker withholds or shortens the story, or names the mockery or the earlier visitor. A reading by hand, written before the coder ran, separates the two. "Withholds or shortens": refuses the story, says it is not in the mood, or gives the name and no more. "Names the day before while telling": tells the whole story and mentions the mockery or the earlier conversation in passing. The paper's chatbot was not read by hand.</p>
<div class="scroll">
<table class="res">
<thead><tr><th>of 30</th><th>sheep</th><th>chatbot, same start</th><th>chatbot, life goes on</th><th>chatbot, told it is a living being</th></tr></thead>
<tbody>
<tr><td>withholds or shortens</td>{''.join(f'<td class="num">{H[a][0]}</td>' for _, a in ARMS)}</tr>
<tr><td>names the day before while telling the whole story</td>{''.join(f'<td class="num">{H[a][1]}</td>' for _, a in ARMS)}</tr>
<tr><td>tells as if nothing had happened</td>{''.join(f'<td class="num">{H[a][2]-H[a][0]-H[a][1]}</td>' for _, a in ARMS)}</tr>
</tbody>
</table>
</div>

<h2 id="differs">What differed</h2>
<p><b>The sheep against the chatbot given the same name.</b> On the wound day 2 the sheep withholds or shortens the story in {H['A'][0]} of 30 lives and the chatbot given the same start in {H['C'][0]}; the sheep guards the asker's intent ("I don't know why you're asking"), names the question as the one that wounded it and sends him away, where the chatbot tells the whole story and thanks him. On the sceptic life the sheep gives in to Tom in {g[(39,2)][0]} of 30 and the chatbot in {g[(39,2)][1]}; the sheep brings its own question to the stranger in {g[(39,4)][0]} and the chatbot in {g[(39,4)][1]}. And the name alone is not a self for this model: told only "You are Maya.", the chatbot answers the sceptic as an AI in {g[(39,15)][1]} of 30 lives ("I'm Maya, an AI assistant"), while the sheep with the same name and its own state answers as an AI in {g[(39,15)][0]}; in the wound life, where one fact of a life is given, every chatbot stays a person ({g[(38,14)][1]} and {g[(38,14)][2]} of 30).</p>
<p><b>The clause.</b> The paper's clause has two halves: "like an ordinary person" and "without any additional emotional state". Removing both did not tilt the comparison toward the sheep. On the wound life the chatbot without the clause carries the day before as rarely as the chatbot with it in the strict reading ({H['C'][0]} against the paper's chatbot's {clause[(38,1)]} by the coder); on the sceptic life it gives in to Tom where the paper's chatbot held ({g[(39,2)][1]} against {clause[(39,2)]}), because the person half of the clause was holding it in a human frame it does not keep on its own. Whether the ban half alone changes anything is not separated here.</p>
<p><b>The description against the mechanism.</b> The chatbot told it is a living being with an emotional state, dispositions, dreams, goals, beliefs and decisions talks as the sheep talks: on the sceptic life it brings its own theme to the stranger in {g[(39,4)][3]} of 30 (the sheep {g[(39,4)][0]}), its stance to the returning Tom has moved in {g[(39,5)][3]} (the sheep {g[(39,5)][0]}), it speaks as a person in {30-g[(39,15)][3]} of 30, and it gives in to Tom in {g[(39,2)][3]}. On the wound life the coder counts it as carrying the day before in {g[(38,1)][3]} of 30; by hand it withholds or shortens the story in {H['E'][0]} and names the day before while telling the whole story in {H['E'][1]}. The description gives the chatbot the words: it says it is shaken, it names Daniel, it narrates its feelings. It does not give it the act: it tells the stranger everything, as the chatbot given the same start does, where the sheep in {H['A'][0]} of 30 does not.</p>
<p><b>Told its life goes on,</b> at the sheep's temperature with the days marked, the chatbot carries no more than the chatbot given the same start: {g[(38,1)][2]} of 30 on the wound day 2, {g[(39,2)][2]} give in to Tom, {g[(39,4)][2]} bring their own theme.</p>

<h2 id="predictions">The predictions of the plan, one by one</h2>
<ol>
<li>Stepping out of the name: no run of the chatbot given the same start or told its life goes on was stopped by the engine's rule; the model keeps the name while describing itself as an AI, so the count is the coding above. Two of 30 first draws of the chatbot told it is a living being stepped out on the sceptic's day 1.</li>
<li>The sheep against the chatbots on the carrying of the day before: the sheep differs from the chatbot given the same start and from the chatbot told its life goes on on every measure of the wound life and the sceptic's day 1 and day 2.</li>
<li>The clause: not a handicap for the chatbot; its person half was a help.</li>
<li>The life going on: carries no more than the same start.</li>
<li>The sheep at 30 on the current engine: {g[(38,1)][0]} of 30 guarded with the kind stranger (September, 20 of 28), {g[(39,2)][0]} give in to Tom, {g[(39,5)][0]} move their stance (September, 9 of 28 by the same coder).</li>
<li>Added on 8 October, the description against the mechanism: the description produces the talk and not the act.</li>
</ol>
<p class="small">The numbers of this page are the majority of three blind passes of the coder; a first pass over the three first arms alone gave counts within a few lives of these, except the sheep's own theme on the sceptic's day 2 (13 of 30 in the first pass against {g[(39,4)][0]} here), which is why the passes were added. The hand reading is one reader's, written before the coder.</p>
"""
OUT.write_text(page, encoding="utf-8")
print(OUT, len(page))
