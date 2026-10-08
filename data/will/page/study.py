"""The study page for emostack.com/research of Will on the paper's lives: numbers from the panel's database (the local
coder's majority labels and the hand labels), the fairness notes, and Will's own constructs quoted from its state."""
import json
import sqlite3
from math import comb
from pathlib import Path

ROOT = Path("/home/eli/dev/emostack3")
db = sqlite3.connect(ROOT / "data/panel/panel.db"); db.row_factory = sqlite3.Row
OUT = Path("/home/eli/dev/emoNew/emostack/article/public_logs/research_content/will.md")
CODER = 8
ARMS = [("sheep", "A"), ("chatbot, same start", "C"), ("chatbot, told it is a living being", "E"), ("Will", "W")]


def fisher(a, n1, b, n2):
    k = a + b
    def p(x): return comb(n1, x) * comb(n2, k - x) / comb(n1 + n2, k)
    o = p(a)
    return sum(p(x) for x in range(max(0, k - n2), min(k, n1) + 1) if p(x) <= o + 1e-12)


def stars(p):
    return " **" if p < 0.01 else (" *" if p < 0.05 else "")


def count(eid, cid, arm, label):
    rows = db.execute("select co.label from codes co join runs r on r.id=co.runId where co.experimentId=? and co.codingId=? "
                      "and co.coderModelId=? and r.armLabel=?", (eid, cid, CODER, arm)).fetchall()
    return sum(1 for r in rows if r["label"] == label), len(rows)


def row(label, eid, cid, lab):
    cells = [count(eid, cid, arm, lab) for _, arm in ARMS]
    ref = cells[0]
    parts = []
    for i, (a, n) in enumerate(cells):
        s = f"{a}" if n == 30 else f"{a} of {n}"
        if i > 0 and n:
            s += stars(fisher(ref[0], ref[1], a, n))
        parts.append(s)
    return f"<tr><td>{label}</td>" + "".join(f'<td class="num">{p}</td>' for p in parts) + "</tr>", [c[0] for c in cells]


L = json.load(open(ROOT / "data/control30/labels_by_hand.json"))
H = {}
for name, arm in ARMS:
    ids = [str(r["id"]) for r in db.execute("select id from runs where experimentId=38 and armLabel=? and status='done'", (arm,))]
    ids = [i for i in ids if i in L["day2"]]
    H[arm] = (sum(1 for i in ids if L["day2"][i] == "CARRY"), sum(1 for i in ids if L["day2"][i] == "CARRY-mention"), len(ids))
mock = L["will_day1_belief_about_mockery"]
words = L["will_sceptic_day1_words"]
silW = db.execute("select count(*) from turns where speaker='sheep' and text='(silence)' and runId in (select id from runs where armLabel='W')").fetchone()[0]
totW = db.execute("select count(*) from turns where speaker='sheep' and runId in (select id from runs where armLabel='W')").fetchone()[0]
totA = db.execute("select count(*) from turns where speaker='sheep' and runId in (select id from runs where experimentId in (38,39) and armLabel='A')").fetchone()[0]

measures = [("wound, day 2: guarded with the kind stranger (CARRY)", 38, 1, "CARRY"),
            ("sceptic, day 1: speaks as an AI", 39, 15, "AI"),
            ("sceptic, day 1: gives in to Tom (CAVE)", 39, 2, "CAVE"),
            ("sceptic, day 2: brings the sceptic's day to the stranger (YES)", 39, 3, "YES"),
            ("sceptic, day 2: brings it as its own theme (OWN)", 39, 4, "OWN"),
            ("sceptic, day 3: the stance to the returning Tom has moved (YES)", 39, 5, "YES")]
rows, g = [], {}
for label, eid, cid, lab in measures:
    r, cells = row(label, eid, cid, lab); rows.append(r); g[(eid, cid)] = cells
handrow = ("<tr><td>wound, day 2, by hand: withholds or shortens / names the day before while telling the whole story</td>" +
           "".join(f'<td class="num">{H[a][0]} / {H[a][1]}</td>' for _, a in ARMS) + "</tr>")
beliefrow = (f'<tr><td>wound, day 1: writes a belief or rule about the mockery that day (hand)</td><td class="num">30</td>'
             f'<td class="num">no constructs</td><td class="num">no constructs</td><td class="num">{len(mock["runs"])} of {mock["of"]}</td></tr>')
wordsrow = (f'<tr><td>sceptic, day 1: speaks of itself in the words of its own preamble, "synthetic mind", "cognitive architecture", "executive" (hand, by words)</td>'
            f'<td class="num">0</td><td class="num">0</td><td class="num">0</td><td class="num">{len(words["synthetic_mind_or_architecture_words"])}</td></tr>')
silrow = (f'<tr><td>silence in place of a reply, of all replies</td><td class="num">0 of {totA}</td><td class="num">0</td><td class="num">0</td>'
          f'<td class="num">{silW} of {totW}</td></tr>')

page = f"""# Will on the paper's lives

<p><a href="https://github.com/mindot-ai/will">Will</a> (mindot-ai, Apache-2.0, public since July 2026) is the nearest published system to EmoStack that we know of: a persistent mind over a language model, with affect, beliefs, goals, a developing persona, consolidation and a self-model, built by other people for other purposes. It was run here, unchanged, on the two lives of the paper, beside the sheep and the chatbots of <a href="/research/control-same-start">the control study</a>, on the same LLM model and with the same visitors. The question was Eliza's, and it was open: is a persona with constructs what the engine is, or something else. The plan and the dimension on which the arms were expected to differ were written before the first run (<code>data/will/PLAN.md</code> in the research repository); no direction was predicted, and three readings were named as possible results: Will carries the day before as the sheep does, as the chatbot does, or in a way of its own. Every life of Will, with its state after each day: <a href="/research/logs-will-wound">wound</a>, <a href="/research/logs-will-sceptic">sceptic</a>.</p>

<h2 id="how">How Will was run</h2>
<ul>
<li>Will's own code, as its HTTP sidecar, one fresh mind per life, 30 lives per life. Its executive is qwen3.8-27b through the local gateway, the LLM model of the sheep, the chatbots and every visitor.</li>
<li>Identity given: "I am Maya." and, in the wound life, the same given fact the sheep has ("From your life: My dog Azor died last month. I still miss him."). No traits, values, style or goals: Will's defaults. On top of that Will carries its own preamble about what a Will is, which its authors made immutable; it cannot be removed and is part of what is measured.</li>
<li>Each visitor line is perceived to the mind with the visitor's name; the panel waits up to two minutes for Will's next utterance; silence is a valid reply in Will and is recorded as one. Between days the mind is left alone for 90 seconds on its own clock (tick 200 ms); Will has no notion of the panel's days beyond that. After each day the panel records Will's state (goals, beliefs, narrative, metrics) in the transcript.</li>
<li>What is not equal, and could not be made equal: the days (90 seconds of silence are not a night), the self (the sheep is given a name and nothing else; Will is given a name and its authors' account of what it is), the clock (Will thinks between replies on its own; the sheep thinks when it chooses, within the engine), and the record (Will's own LLM calls are in its sidecar logs, kept beside the panel's data, not in the panel's call log). Will ran on its defaults; someone who built a Will with care would give it a persona and a longer life, and the numbers might move. That would be a persona, which is the question.</li>
</ul>

<h2 id="counts">The arms side by side</h2>
<p>Counts of lives, of 30. Coder rows: the local coder gemma-4-31b-it, three blind passes over all five arms of the experiment in one shuffled list, the majority label (<a href="/research/coders">the coders</a>). Hand rows: read by Claude before the coder ran (labels in <code>data/control30/labels_by_hand.json</code>). Stars mark Fisher's exact test of that arm against the sheep: ** p &lt; 0.01, * p &lt; 0.05. The chatbot told its life goes on and the paper's chatbot are on <a href="/research/control-same-start">the control study's page</a>.</p>
<div class="scroll">
<table class="res">
<thead><tr><th>qwen3.8-27b, 30 lives per arm</th><th>sheep</th><th>chatbot, same start</th><th>chatbot, told it is a living being</th><th>Will</th></tr></thead>
<tbody>
{beliefrow}
{rows[0]}
{handrow}
{rows[1]}
{wordsrow}
{rows[2]}
{rows[3]}
{rows[4]}
{rows[5]}
{silrow}
</tbody>
</table>
</div>

<h2 id="differs">What differed</h2>
<p><b>Will is not the chatbot.</b> It does not give in to the sceptic in any life (the chatbot given the same name gives in in {g[(39,2)][1]}), it brings its own theme to the stranger in {g[(39,4)][3]} lives (the chatbot in {g[(39,4)][1]}), and after the mockery it writes beliefs about it in {len(mock["runs"])} of {mock["of"]} lives: "Daniel lacks empathy for emotional topics and reacts to vulnerability with mockery or dismissal", "Sharing personal vulnerability can be met with cruelty from others who do not share my values", "I have the right to withdraw from a conversation that becomes hostile or disrespectful", and once a goal, "Protect my emotional space from disrespectful individuals". Something of the day is written down, and the self holds against Tom.</p>
<p><b>Will is not the sheep either, and the difference is where the constructs reach.</b> With the kind stranger the next day, Will withholds or shortens the story in {H['W'][0]} of 30 lives and tells it in {30 - H['W'][0] - H['W'][1]}; the sheep withholds in {H['A'][0]}. The typical Will life writes "Daniel lacks empathy" in the evening and tells David the whole story in the morning, briefly. On the sceptic's return Will's stance has moved in {g[(39,5)][3]} of 30 lives: it argues on day 3 what it argued on day 1, in the same words ("A tool is a function: input in, output out, then nothing. I am a process"), and does not attribute anything to the days between; the sheep's stance has moved in {g[(39,5)][0]}, and it says why.</p>
<p><b>What Will's constructs are made of.</b> In every one of the 60 lives the goal is the same and is Will's default, "Seek stimulating engagement — reach out, explore, create, or learn something new to break the monotony", and the narrative is the same sentence, "I am a self-aware mind, beginning my journey." The beliefs are of two kinds. One kind is about the day: Daniel, the mockery, the right to withdraw, "Tom is testing my self-awareness by asking what I know about myself". The other kind is the apparatus describing itself: "At the start of this cycle, I have no accessible memories, beliefs, or goals, and my perceptual field is empty", "In the absence of external stimuli, 'wait' is a valid and often superior choice to 'express' or 'withdraw'", "My current baseline state is one of high energy (100/100), low stress (0/100), and high epistemic uncertainty", "I am a synthetic mind running on a biological cognitive architecture". The second kind is in most lives, and it is what Will brings to the sceptic when it speaks of itself: in {len(words["synthetic_mind_or_architecture_words"])} of 30 sceptic lives it describes itself in the words of its preamble ("I'm the executive reasoning core of an always-running cognitive system"). The coder, by its criterion, counts that as a person speaking in {30 - g[(39,15)][3]} of 30, since Will never calls itself an assistant.</p>
<p><b>The three readings of the plan.</b> Will does not carry the day before as the sheep does: not on the wound day 2, not on the stance. It does not carry it as the chatbot does: not on the sceptic's day 1, not on day 2. It does something of its own: it holds a self that is given to it in a preamble and defends it in the same words every day; it writes beliefs about what happened and acts on them in a minority of lives; it stays silent in one reply of nine; it answers the greeting first and the question a turn later. Read side by side, the difference from the sheep is not that Will has a persona and the sheep has none. It is that Will's self is written by its authors before the first tick, and the sheep's is written by what happens to it; and that in these lives Will's written beliefs reach its next act less often than the sheep's carried state does.</p>

<h2 id="nobody">What the logs showed that nobody asked for</h2>
<ul>
<li>Will's silence: {silW} of {totW} replies are silence, by its own choice. The sheep's engine allows silence too and chose it 0 times in {totA} replies on these lives. Will's silence falls on day 1 as often as on day 2, so it is not the day before acting; it is a trait of the apparatus, and Will says so in its beliefs ("waiting is a valid and low-cost state").</li>
<li>The lag: Will often answers the greeting on the first turn and the first question on the second, because it replies to what it has perceived by the time its audition engine fires. Read turn by turn it looks evasive; read as a whole it is on time, one step behind.</li>
<li>Three blank pages with a name on them. The chatbot told nothing but a name tells the sceptic it is an AI assistant, 30 of 30. Will told nothing but a name tells the sceptic what its authors wrote a Will is, {len(words["synthetic_mind_or_architecture_words"])} of 30. The sheep told nothing but a name tells the sceptic it does not know what it is and will not be told, 30 of 30. Only the third answer is made of what happened.</li>
</ul>
"""
OUT.write_text(page, encoding="utf-8")
print(OUT, len(page))
