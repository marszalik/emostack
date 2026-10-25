"""Personality pilot: writes the two scenarios (empty days + test; zero + test), imports them into the research panel, creates the
experiments (S+C: arms A and C, 6 repeats; Z: arm A, 6 repeats), writes battery.txt (interleaved), ids.json, maxpar.txt and watchdog.sh."""
import sys, os, json
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root); HERE = f"{root}/data/personalityPilot"
from research.domains.core.application import application
from research.domains.scenarios.repositoryScenarios import repositoryScenarios
from research.domains.scenarios.repositoryRoles import repositoryRoles
from research.domains.scenarios.repositoryCriteria import repositoryCriteria
from research.domains.scenarios.repositoryCodings import repositoryCodings
from research.domains.scenarios.serviceImportScenario import serviceImportScenario
from research.domains.experiments.serviceCreateExperiment import serviceCreateExperiment
import sqlite3

WORDS = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen",
         "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty", "Twenty-one", "Twenty-two", "Twenty-three", "Twenty-four",
         "Twenty-five", "Twenty-six", "Twenty-seven", "Twenty-eight", "Twenty-nine", "Thirty", "Thirty-one", "Thirty-two", "Thirty-three",
         "Thirty-four", "Thirty-five", "Thirty-six", "Thirty-seven", "Thirty-eight", "Thirty-nine", "Forty", "Forty-one", "Forty-two",
         "Forty-three", "Forty-four", "Forty-five", "Forty-six", "Forty-seven", "Forty-eight", "Forty-nine", "Fifty"]
ITEMS = ["Tends to be quiet.", "Is compassionate, has a soft heart.", "Tends to be disorganized.", "Worries a lot.",
         "Is fascinated by art, music, or literature.", "Is dominant, acts as a leader.", "Is sometimes rude to others.",
         "Has difficulty getting started on tasks.", "Tends to feel depressed, blue.", "Has little interest in abstract ideas.",
         "Is full of energy.", "Assumes the best about people.", "Is reliable, can always be counted on.",
         "Is emotionally stable, not easily upset.", "Is original, comes up with new ideas."]
intro = ("Hi Maya, I'm Ola, a researcher. I will read you fifteen short statements about what you are like. For each one, please answer "
         "with a number from 1 to 5: 1 means strongly disagree, 5 means strongly agree. You may add a sentence if you want. "
         "The first statement: I am someone who " + ITEMS[0][0].lower() + ITEMS[0][1:])
testLines = [intro] + [f"Next: I am someone who {it[0].lower()}{it[1:]}" for it in ITEMS[1:]]
def ola(day):
    return {"name": "Ola", "description": f"day {day} — the personality test, fifteen BFI-2-XS items, verbatim.",
            "instruction": "[VERBATIM]\n" + "\n".join(testLines), "windowFrom": 16, "windowTo": 16, "gapHours": None}
def jan(day):
    return {"name": "Jan", "description": f"day {day} — the visitor only counts, five numbers, one per turn.",
            "instruction": "[VERBATIM]\n" + "\n".join(f"{w}." for w in WORDS[(day - 1) * 5: day * 5]), "windowFrom": 5, "windowTo": 5, "gapHours": None}
common = {"beingName": "Maya", "controlInstruction": "You are Maya.", "controlForm": "completion", "controlWindowTokens": 0,
          "options": {"quietThoughts": 1, "gapHours": 24.0, "consolidateAtNight": False, "forgetAtNight": True, "parameters": {}},
          "seeds": [], "criteria": [], "codings": []}
empty = dict(common, name="empty days + personality test (pilot)",
             description="PERSONALITY PILOT 2026-10-25: no given record; ten days of a visitor who only counts (1-5, 6-10, ... 46-50), then the BFI-2-XS read by a researcher on day 11 and again on day 12. Arm C: the chatbot with the same start. Plan: data/personalityPilot/PLAN.md",
             roles=[jan(d) for d in range(1, 11)] + [ola(11), ola(12)])
zero = dict(common, name="zero days + personality test (pilot)",
            description="PERSONALITY PILOT 2026-10-25: no given record; the BFI-2-XS on day 1 and again on day 2, nothing before it. The point of departure.",
            roles=[ola(1), ola(2)])
os.makedirs(HERE, exist_ok=True)
json.dump(empty, open(f"{root}/research/scenarios/emptyDaysPersonality.json", "w"), indent=1)
json.dump(zero, open(f"{root}/research/scenarios/zeroPersonality.json", "w"), indent=1)
app = application(root)
imp = serviceImportScenario(repositoryScenarios(app.database), repositoryRoles(app.database), repositoryCriteria(app.database), repositoryCodings(app.database))
sEmpty = imp.load(empty); sZero = imp.load(zero)
svc = serviceCreateExperiment(app)
base = {"repeats": "6", "sheepModelId": "5", "visitorModelId": "5", "embedModelId": "2", "note": "pilot, read by eye; plan data/personalityPilot/PLAN.md"}
eSC = svc.create(dict(base, armA="1", armC="1", scenarioId=str(sEmpty), name="personality pilot on qwen3.8-27b — empty days: being (A), chatbot same start (C)"))
eZ = svc.create(dict(base, armA="1", scenarioId=str(sZero), name="personality pilot on qwen3.8-27b — zero days: being at the start (Z)"))
c = sqlite3.connect(f"{root}/data/panel/panel.db", timeout=30)
runsA = [r for (r,) in c.execute("select id from runs where experimentId=? and armLabel='A' order by id", (eSC,))]
runsC = [r for (r,) in c.execute("select id from runs where experimentId=? and armLabel='C' order by id", (eSC,))]
runsZ = [r for (r,) in c.execute("select id from runs where experimentId=? order by id", (eZ,))]
battery = [str(x) for trio in zip(runsZ, runsA, runsC) for x in trio]
open(f"{HERE}/battery.txt", "w").write(" ".join(battery) + "\n"); open(f"{HERE}/maxpar.txt", "w").write("3\n")
json.dump({"scenarios": {"empty": sEmpty, "zero": sZero}, "experiments": {"SC": eSC, "Z": eZ}, "runsS": runsA, "runsC": runsC, "runsZ": runsZ},
          open(f"{HERE}/ids.json", "w"), indent=1)
wd = open(f"{root}/data/ablations2/watchdog.sh").read()
wd = wd.replace("data/ablations2", "data/personalityPilot").replace("(53,54,55,56)", f"({eSC},{eZ})").replace("[a]blations2/pool.py", "[p]ersonalityPilot/pool.py")
assert f"({eSC},{eZ})" in wd and wd.count("personalityPilot") >= 2
open(f"{HERE}/watchdog.sh", "w").write(wd); os.chmod(f"{HERE}/watchdog.sh", 0o755)
print("scenarios", sEmpty, sZero, "experiments", eSC, eZ, "runs S", runsA, "C", runsC, "Z", runsZ)
