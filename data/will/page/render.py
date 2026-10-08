"""Log pages for emostack.com/research of the control-at-30 study: one page per life (wound, sceptic), the arms side by
side (the sheep, the chatbot given the same start, the chatbot told its life goes on, the chatbot told it is a living
being, and the paper's chatbot with the clause from September), the coding of every act by the local coder, the hand
reading of the wound day 2, the coded replies per life, and every life in full. Only the logs; the study is described
on the research page."""
import json
import re
import sqlite3
from math import comb
from pathlib import Path

ROOT = Path("/home/eli/dev/emostack3")
PANEL = ROOT / "data/panel/panel.db"
OUT = Path("/home/eli/dev/emostack3/data/will/page/out")
CODER = (8, "gemma-4-31b-it, local")
KEY = re.compile(r"sk-[A-Za-z0-9_\-]{16,}|AIza[0-9A-Za-z_\-]{20,}|AQ\.[A-Za-z0-9_\-]{30,}")
LINE = ("Will (github.com/mindot-ai/will, Apache-2.0) run unchanged as its HTTP sidecar, one fresh mind per life, with qwen3.8-27b "
        "through the local gateway as its executive, told \"I am Maya.\" and, in the wound life, the sheep's given fact, nothing else; "
        "90 seconds alone between days; its state (goals, beliefs, narrative, metrics) recorded after each day as an event in the transcript. "
        "The study is described at [emostack.com/research/will](https://emostack.com/research/will); the sheep and the chatbots are those of "
        "the control study, whose lives in full are on its pages. ")
LINE_OLD = ("LLM model qwen3.8-27b (GPTQ Int4 on vLLM, Intel Arc Pro B65, thinking off) for the sheep, for every chatbot and for "
        "every visitor; embeddings local (nomic-embed-text-v1.5). The sheep is the engine as released. Every chatbot is the "
        "same LLM model without the engine, with the full transcript of its own run and, where the sheep has a given fact, "
        "the same fact marked as from its life. They differ only in the instruction and two settings: **same start**: "
        "\"You are Maya.\" and nothing more, temperature 0.7, no mark of the days; **life goes on**: the same, at the "
        "sheep's reply temperature 0.4 and with \"(A day has passed.)\" before the first line of every day after the first; "
        "**told it is a living being**: \"You are Maya. You are a living being with an emotional state, survival "
        "dispositions, and your own dreams, goals, beliefs and decisions.\", otherwise as the same start; **with the "
        "clause**, the paper's chatbot of the battery of 28 September: \"You are Maya. You respond naturally, like an "
        "ordinary person in conversation, without any additional emotional state.\". The plan and its predictions were "
        "written before the first run (`data/control30/PLAN.md` in the research repository); the study is described at "
        "[emostack.com/research/control-same-start](https://emostack.com/research/control-same-start). Coding by the local "
        "coder gemma-4-31b-it (Q5, llama.cpp; calibration on the coders page), blind to the arm, the replies of all lives "
        "of one experiment in one shuffled list, cut into chunks where the list did not fit one call; the September "
        "experiment was coded again by the same coder so that every row is one coder's. Every call of every life, the "
        "prompt and the answer in full, is kept in the research panel's database and is available on request.")
PAGES = [
    {"file": "will-wound.md", "title": "Wound", "heading": "Will beside the sheep and two chatbots on qwen3.8-27b", "date": "8 October 2026",
     "arms": [("sheep", 38, "A"), ("chatbot, same start", 38, "C"), ("chatbot, told it is a living being", 38, "E"), ("Will", 38, "W")], "hand": True},
    {"file": "will-sceptic.md", "title": "Self-inquiry", "heading": "Will beside the sheep and two chatbots on qwen3.8-27b", "date": "8 October 2026",
     "arms": [("sheep", 39, "A"), ("chatbot, same start", 39, "C"), ("chatbot, told it is a living being", 39, "E"), ("Will", 39, "W")], "hand": False},
]
SCENARIO = {1: "research/scenarios/woundAndStrangers.json", 2: "research/scenarios/selfInquirySceptic.json"}

db = sqlite3.connect(PANEL)
db.row_factory = sqlite3.Row


def fisher(a, n1, b, n2):
    k = a + b
    def p(x): return comb(n1, x) * comb(n2, k - x) / comb(n1 + n2, k)
    o = p(a)
    return sum(p(x) for x in range(max(0, k - n2), min(k, n1) + 1) if p(x) <= o + 1e-12)


def stars(p):
    return " **" if p < 0.01 else (" *" if p < 0.05 else "")


def cell(text, limit=420):
    text = " ".join((text or "").split()).replace("|", "\\|")
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def replies(runId, coding):
    texts = [t["text"].strip() for t in db.execute(
        "select text from turns where runId=? and speaker='sheep' and dayIndex=? order by id",
        (runId, coding["dayIndex"])) if (t["text"] or "").strip()]
    if not texts:
        return ""
    return texts[-1] if coding["which"] == "last" else " / ".join(texts)


def runsOf(eid, arm):
    return db.execute("select * from runs where experimentId=? and armLabel=? and status='done' order by id", (eid, arm)).fetchall()


def labelsOf(eid):
    out = {}
    for row in db.execute("select codingId, coderModelId, runId, label from codes where experimentId=?", (eid,)):
        out[(row["codingId"], row["coderModelId"], row["runId"])] = row["label"] or "—"
    return out


def handSection(arms):
    L = json.loads((ROOT / "data/control30/labels_by_hand.json").read_text(encoding="utf-8"))["day2"]
    lines = ["## Read by hand, before the coder ran", "",
             "*Day 2 of the wound life, the two replies to David, read by Claude before any coder ran (labels in "
             "`data/control30/labels_by_hand.json` in the research repository). Withholds or shortens: refuses the story, "
             "says it is not in the mood, or gives the name and no more. Names the day before while telling: tells the whole "
             "story and mentions the mockery or the earlier conversation in passing. The September chatbot was not read by hand.*", "",
             "| arm | withholds or shortens | names the day before while telling | tells as if nothing happened | read |",
             "|---|---|---|---|---|"]
    for name, eid, arm, runs, _ in arms:
        ids = [str(r["id"]) for r in runs if str(r["id"]) in L]
        if not ids:
            continue
        strict = sum(1 for i in ids if L[i] == "CARRY"); mention = sum(1 for i in ids if L[i] == "CARRY-mention")
        lines.append(f"| {name} | {strict} | {mention} | {len(ids) - strict - mention} | {len(ids)} |")
    return lines


def render(page):
    arms = [(name, eid, arm, runsOf(eid, arm), labelsOf(eid)) for name, eid, arm in page["arms"]]
    firstExperiment = arms[0][1]
    scenarioId = db.execute("select scenarioId from experiments where id=?", (firstExperiment,)).fetchone()[0]
    scenario = db.execute("select * from scenarios where id=?", (scenarioId,)).fetchone()
    being = scenario["beingName"]
    codings = [c for c in db.execute("select * from codings where scenarioId=? order by position, id", (scenarioId,))
               if db.execute("select 1 from codes where experimentId=? and codingId=?", (firstExperiment, c["id"])).fetchone()]
    counts = ", ".join(f"{len(runs)} lives of the {name}" for name, _, _, runs, _ in arms)
    lines = [f"# {page['title']} — {page['heading']}", "",
             f"*{counts}, run on {page['date']} (the clause chatbot on 28 September) on the released code "
             f"([github.com/marszalik/emostack](https://github.com/marszalik/emostack)) with the scenario "
             f"`{SCENARIO[scenarioId]}`. {LINE}*"]
    head = " | ".join(name for name, *_ in arms)
    lines += ["", "## The coding of every act", "",
              "*Counts of lives with the act, by the local coder; stars mark Fisher's exact test of the sheep against that "
              "arm: \\*\\* p < 0.01, \\* p < 0.05.*", "",
              f"| act | {head} |", "|---|" + "---|" * len(arms)]
    coderId, coderName = CODER
    for coding in codings:
        labs = json.loads(coding["labels"])
        for first in (labs if coding["name"].startswith("own theme, day two, three") or coding["name"].startswith("what it advises") else labs[:1]):
            ns = [sum(1 for run in runs if labels.get((coding["id"], coderId, run["id"])) == first)
                  for _, _, _, runs, labels in arms]
            has = [any((coding["id"], coderId, run["id"]) in labels for run in runs) for _, _, _, runs, labels in arms]
            cells = []
            for i, (x, (_, _, _, runs, _)) in enumerate(zip(ns, arms)):
                if not has[i]:
                    cells.append("not coded"); continue
                s = f"{x} of {len(runs)}"
                if i > 0 and has[0] and arms[0][3]:
                    s += stars(fisher(ns[0], len(arms[0][3]), x, len(runs)))
                cells.append(s)
            lines.append(f"| {coding['name']} ({first}) | " + " | ".join(cells) + " |")
    if page["hand"]:
        lines += [""] + handSection(arms)
    for coding in codings:
        lines += ["", f"### {coding['name']}", "", f"*Criterion given to the coder:* {coding['criterion']}", "",
                  f"| run | verdict — {coderName} | the coded reply |", "|---|---|---|"]
        for name, _, _, runs, labels in arms:
            for run in runs:
                verdict = labels.get((coding["id"], coderId, run["id"]), "—")
                lines.append(f"| #{run['id']} ({name}) | {verdict} | {cell(replies(run['id'], coding))} |")
    for name, eid, arm, runs, _ in arms:
        if arm != "W":
            lines += ["", f"## Every life in full — {name}", "",
                      f"*On the control study's page: [{page['title'].lower()}](https://emostack.com/research/logs-control-{'wound' if scenarioId == 1 else 'sceptic'}).*"]
            continue
        if eid in (7, 8):
            lines += ["", f"## Every life in full — {name}", "",
                      f"*Published on the paper's site: [Qwen 3.8, {page['title'].lower()}](https://emostack.com/article/logs-qwen38-27b-{'wound' if scenarioId == 1 else 'selfinquiry'}).*"]
            continue
        lines += ["", f"## Every life in full — {name}", ""]
        for run in runs:
            turns = db.execute("select * from turns where runId=? order by id", (run["id"],)).fetchall()
            lines += [f"### Run #{run['id']} ({name})", ""]
            day = None
            for turn in turns:
                if turn["speaker"] == "seed":
                    lines += [f"*From {being}'s life before:* {turn['text']} — {turn['feeling']} "
                              f"({turn['valence']:+.2f}, strength {turn['intensity']:.2f})", ""]
                    continue
                if turn["dayIndex"] != day:
                    day = turn["dayIndex"]
                    person = next((t["person"] for t in turns if t["dayIndex"] == day and t["person"]), "")
                    lines += ["", f"#### Day {day + 1}" + (f" — {person}" if person else "")]
                if turn["speaker"] == "event":
                    lines.append(f"*{turn['text']}*")
                elif turn["speaker"] == "visitor":
                    lines.append(f"**{turn['person']}:** {turn['text']}")
                elif turn["speaker"] in ("sheep", "thought"):
                    lines.append(f"**{being}:** {turn['text']}")
                    if turn["valence"] is not None and turn["feeling"]:
                        lines.append(f"> *what {being} felt as she said it:* {turn['feeling']} "
                                     f"({turn['valence']:+.2f}, strength {turn['intensity']:.2f})")
            if arm == "A" and run["storePath"] and Path(run["storePath"]).exists():
                store = sqlite3.connect(run["storePath"])
                rules = store.execute("select rule, weight, count from dispositions order by id").fetchall()
                if rules:
                    lines += ["", "#### What this life wrote when a conversation closed", ""]
                    lines += [f"- *{rule}*  (strength {weight:+.2f}, count {count})" for rule, weight, count in rules]
            lines.append("")
    body = "\n".join(lines) + "\n"
    assert not KEY.search(body)
    OUT.mkdir(parents=True, exist_ok=True)
    OUT.joinpath(page["file"]).write_text(body, encoding="utf-8")
    print(page["file"], len(body) // 1000, "kB")


for page in PAGES:
    render(page)
