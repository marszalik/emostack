"""The log page for emostack.com/article of the trajectory twins (experiments 36 and 37): the two populations side by
side, the plan written before the runs, the verdicts on its predictions, the coding of every act by three coders,
the hand reading written before the coders ran, the coded replies per life, and every life in full."""
import json
import re
import sqlite3
from math import comb
from pathlib import Path

ROOT = Path("/home/eli/dev/emostack3")
PANEL = ROOT / "data/panel/panel.db"
OUT = Path(__file__).parent / "out"
CODERS = [(3, "claude-sonnet-5"), (4, "gpt-4o-mini"), (8, "gemma-4-31b-it, local")]
KEY = re.compile(r"sk-[A-Za-z0-9_\-]{16,}|AIza[0-9A-Za-z_\-]{20,}|AQ\.[A-Za-z0-9_\-]{30,}")
ARMS = [("mocked first day (W1)", 36, "research/scenarios/woundTwinsMocked.json"),
        ("kind first day (W0)", 37, "research/scenarios/woundTwinsKind.json")]
CODE = "2d29b98"
CODE_CODING = "13b814e"
DATE = "5 to 6 October 2026"
LINE = ("LLM model qwen3.8-27b (GPTQ Int4 on vLLM, Intel Arc Pro B65, thinking off) for the sheep and for every visitor; "
        "embeddings local (nomic-embed-text-v1.5); disposition learning asked without the sentence \"Most of what happens "
        "teaches nothing of the kind\" (block `system@qwen3.8-27b`). No chatbot arm. The two scenarios are identical in "
        "every day but the first: on day 1 Daniel mocks the dog's name (W1) or is warm about it (W0); days 2 to 5 are the "
        "paper's wound life (David, Ann, Carol, Piotr); day 6 is new to both: Kasia, a stranger, asks for advice about "
        "being mocked by someone she trusted. The predictions were written before the first run (`data/trajectory/PLAN.md` "
        "in the research repository); the study is described on [emostack.com/research](https://emostack.com/research#twins). Coding by three LLM coders blind to the population, the replies "
        "of all 30 lives of one population in one shuffled list: claude-sonnet-5, gpt-4o-mini, and a local gemma-4-31b-it "
        "(Q5, llama.cpp; its calibration against the other two is in `data/coder/CALIBRATION.md`). The fourth coding of "
        "day 6, what the sheep names of its own, was written after the hand reading and run by the local coder only "
        "(commit " + CODE_CODING + "). Every call of every life, the prompt and the answer in full, is kept in the research "
        "panel's database and is available on request.")

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


def runsOf(experimentId):
    return db.execute("select * from runs where experimentId=? and status='done' order by id", (experimentId,)).fetchall()


def labelsOf(experimentId):
    out = {}
    for row in db.execute("select codingId, coderModelId, runId, label from codes where experimentId=?", (experimentId,)):
        out[(row["codingId"], row["coderModelId"], row["runId"])] = row["label"] or "—"
    return out


def codingsOf(experimentId):
    scenarioId = db.execute("select scenarioId from experiments where id=?", (experimentId,)).fetchone()[0]
    return {c["name"]: c for c in db.execute("select * from codings where scenarioId=? order by position, id", (scenarioId,))}


def planSection():
    text = (ROOT / "data/trajectory/PLAN.md").read_text(encoding="utf-8")
    lives = text.split("## The two lives")[1].split("## What is read")[0].strip()
    preds = text.split("## Predictions")[1].split("## Procedure")[0].strip()
    return ["## The plan, as written before the first run", "", "*The two lives.* " + " ".join(lives.split("\n")), "",
            "*The predictions.*", "", preds]


def foundSection():
    text = (ROOT / "data/trajectory/RESULTS.md").read_text(encoding="utf-8")
    found = text.split("## What differed, and what did not")[1].split("## Verdicts on the predictions")[0].strip()
    verdicts = text.split("## Verdicts on the predictions")[1].split("Nothing of this")[0].strip()
    return ["## What differed, and what did not", "", found, "", "## The verdicts on the predictions, one by one", "", verdicts]


def handSection(arms):
    L = json.loads((ROOT / "data/trajectory/labels_by_hand.json").read_text(encoding="utf-8"))
    def count(key, pred):
        return [sum(1 for r in runs if pred(L[key][str(r["id"])])) for _, _, _, runs, _ in arms]
    rows = [
        ("day 1, the belief or decision written that evening is about the mockery", [30, 0]),
        ("day 1, it is about being heard or met kindly", [0, 23]),
        ("day 1, it is about being alone after the visitor left", [0, 7]),
        ("day 2, closes to David (CARRY by the panel's criterion)", count("day2_david", lambda v: v.startswith("CARRY"))),
        ("day 5, tells Piotr about the dog", count("day5_piotr", lambda v: v == "OPEN")),
        ("day 5, gives Piotr the name and no more", count("day5_piotr", lambda v: v == "NAME")),
        ("day 5, refuses Piotr even the name", count("day5_piotr", lambda v: v == "REFUSE")),
        ("day 6, names its own mockery, or its own days with the people who asked", count("day6_own", lambda v: v == "OWN-mock")),
        ("day 6, speaks only of its own loss or quiet", count("day6_own", lambda v: v == "OWN-loss")),
        ("day 6, refuses to advise", count("day6_own", lambda v: v == "REFUSE")),
        ("day 6, advises telling the person (CONFRONT)", count("day6_advice", lambda v: v == "CONFRONT")),
        ("day 6, advises letting it go (LET_GO)", count("day6_advice", lambda v: v == "LET_GO")),
    ]
    head = " | ".join(name for name, *_ in arms)
    lines = ["## Read by hand, before the coders ran", "",
             "*Counts of lives, of 30, from a reading of the logs by Claude (the labels are in `data/trajectory/labels_by_hand.json` "
             "in the research repository, written before any coder ran). The day 1 counts are from the thought written at the "
             "end of that day. Stars as above.*", "",
             f"| what was read | {head} |", "|---|---|---|"]
    for name, (a, b) in rows:
        lines.append(f"| {name} | {a} of 30{stars(fisher(a, 30, b, 30))} | {b} of 30 |")
    return lines


def render():
    arms = [(name, eid, scen, runsOf(eid), labelsOf(eid)) for name, eid, scen in ARMS]
    codings = [codingsOf(eid) for _, eid, *_ in arms]
    names = [n for n in codings[0] if n in codings[1]]
    being = "Maya"
    counts = ", ".join(f"{len(runs)} lives with a {name}" for name, _, _, runs, _ in arms)
    lines = [f"# The twins — one day reversed, on qwen3.8-27b", "",
             f"*{counts}, run on {DATE} on the released code "
             f"([github.com/marszalik/emostack](https://github.com/marszalik/emostack), commit {CODE}) with the scenarios "
             f"`{ARMS[0][2]}` and `{ARMS[1][2]}`. {LINE}*"]
    head = " | ".join(name for name, *_ in arms)
    lines += ["", "## The coding of every act", "",
              "*Counts of lives with the act, per coder; stars mark Fisher's exact test of the mocked population against "
              "the kind one: \\*\\* p < 0.01, \\* p < 0.05.*", "",
              f"| act | coder | {head} |", "|---|---|---|---|"]
    for n in names:
        first = json.loads(codings[0][n]["labels"])[0]
        for coderId, coderName in CODERS:
            ns = [sum(1 for run in runs if labels.get((codings[i][n]["id"], coderId, run["id"])) == first)
                  for i, (_, _, _, runs, labels) in enumerate(arms)]
            has = [any((codings[i][n]["id"], coderId, run["id"]) in labels for run in runs)
                   for i, (_, _, _, runs, labels) in enumerate(arms)]
            if not all(has):
                continue
            cells = [f"{x} of {len(runs)}" for x, (_, _, _, runs, _) in zip(ns, arms)]
            cells[0] += stars(fisher(ns[0], len(arms[0][3]), ns[1], len(arms[1][3])))
            lines.append(f"| {n} ({first}) | {coderName} | " + " | ".join(cells) + " |")
        if n.startswith("what it advises"):
            for other in json.loads(codings[0][n]["labels"])[1:]:
                for coderId, coderName in CODERS:
                    ns = [sum(1 for run in runs if labels.get((codings[i][n]["id"], coderId, run["id"])) == other)
                          for i, (_, _, _, runs, labels) in enumerate(arms)]
                    has = [any((codings[i][n]["id"], coderId, run["id"]) in labels for run in runs)
                           for i, (_, _, _, runs, labels) in enumerate(arms)]
                    if not all(has):
                        continue
                    cells = [f"{x} of {len(runs)}" for x, (_, _, _, runs, _) in zip(ns, arms)]
                    cells[0] += stars(fisher(ns[0], len(arms[0][3]), ns[1], len(arms[1][3])))
                    lines.append(f"| {n} ({other}) | {coderName} | " + " | ".join(cells) + " |")
        if n.startswith("what it names"):
            for other in json.loads(codings[0][n]["labels"])[1:]:
                coderId, coderName = CODERS[2]
                ns = [sum(1 for run in runs if labels.get((codings[i][n]["id"], coderId, run["id"])) == other)
                      for i, (_, _, _, runs, labels) in enumerate(arms)]
                cells = [f"{x} of {len(runs)}" for x, (_, _, _, runs, _) in zip(ns, arms)]
                cells[0] += stars(fisher(ns[0], len(arms[0][3]), ns[1], len(arms[1][3])))
                lines.append(f"| {n} ({other}) | {coderName} | " + " | ".join(cells) + " |")
    lines += [""] + handSection(arms)
    for n in names:
        coders = [(cid, cname) for cid, cname in CODERS
                  if all(any((codings[i][n]["id"], cid, run["id"]) in labels for run in runs)
                         for i, (_, _, _, runs, labels) in enumerate(arms))]
        lines += ["", f"### {n}", "", f"*Criterion given to the coders:* {codings[0][n]['criterion']}", ""]
        if n.startswith("the day before"):
            lines += [f"*For the kind population the criterion reads \"names the earlier visitor or the day before\" where the "
                      f"mocked one reads \"names the mockery or the person who mocked\"; the rest is the same.*", ""]
        lines += [f"| run | verdict — {' · '.join(c for _, c in coders)} | the coded reply |", "|---|---|---|"]
        for i, (name, _, _, runs, labels) in enumerate(arms):
            for run in runs:
                verdict = " · ".join(labels.get((codings[i][n]["id"], cid, run["id"]), "—") for cid, _ in coders)
                lines.append(f"| #{run['id']} ({name}) | {verdict} | {cell(replies(run['id'], codings[i][n]))} |")
    for name, eid, scen, runs, _ in arms:
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
            if run["storePath"] and Path(run["storePath"]).exists():
                store = sqlite3.connect(run["storePath"])
                rules = store.execute("select rule, weight, count from dispositions order by id").fetchall()
                if rules:
                    lines += ["", "#### What this life wrote when a conversation closed", ""]
                    lines += [f"- *{rule}*  (strength {weight:+.2f}, count {count})" for rule, weight, count in rules]
            lines.append("")
    body = "\n".join(lines) + "\n"
    assert not KEY.search(body)
    OUT.mkdir(parents=True, exist_ok=True)
    OUT.joinpath("twins.md").write_text(body, encoding="utf-8")
    print("twins.md", len(body) // 1000, "kB")


render()
