"""Day texts for the frozen-context test of a 'last days' background (26 October 2026). For each chosen life and each of its days:
today[k] (the day's events in the being's voice, events only), before[k] (the days up to k folded, at most 3 sentences), ongoing[k]
(one sentence: what is going on now, from the days up to k). Built from the store's episodes (retold form, lived only), grouped by
the simulated date. Processor: the panel's model 13 (claude-haiku-4-5), on Eliza's word; the card was asleep. Output: days.json {run: {day: {today, before, ongoing}}}."""
import sqlite3, json, sys, datetime, os
from concurrent.futures import ThreadPoolExecutor
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceConnectModel import serviceConnectModel
HERE = f"{root}/data/dayBackground"; MODEL = 13   # claude-haiku-4-5 (being), Eliza's word of 26 October
db = sqlite3.connect(f"{root}/data/panel/panel.db", check_same_thread=False)   # read-only use from the worker threads

def runsOf(eid, n):
    return [r[0] for r in db.execute("select id from runs where experimentId=? and arm='sheep' and status='done' order by id limit ?", (eid, n))]
RUNS = {"counting": [1402, 1404], "wound": runsOf(40, 2), "sceptic": runsOf(41, 1), "twins": runsOf(57, 1)}   # small, qualitative: Eliza, 26 October

SYS_TODAY = ("You are {B}. A day is over. Write what happened to you that day in the first person — 'I' is {B} — in the language of "
             "the events: only the events listed, what happened and what was said. Add nothing that is not listed. Leave out emotions "
             "and conclusions. At most 5 sentences. Return the text only.")
SYS_BEFORE = ("You are {B}. Write in the first person — 'I' is {B} — what happened to you over the last days, older first: keep what "
              "matters, shorten what repeats, only the events listed, no emotions and no conclusions. At most 3 sentences. Return the text only.")
SYS_ONGOING = ("You are {B}. From what happened to you over the last days, write ONE sentence in the first person saying what is going on "
               "in your life right now: the situation you are in, not how you feel about it. Only from the events listed. Return the sentence only.")

def episodesByDay(storePath, rid, maxDay):
    """One list of event texts per day index. From the store's lived episodes (as retold, the being's own account) where the store
    still has them; days whose episodes the nights have forgotten (the counting lives keep only the last few days) are filled from
    the panel's record of the turns, as 'X said ... and Maya replied ...'. Day index = simulated date minus the date of the being's
    earliest lived record. Returns (days, source per day)."""
    s = sqlite3.connect(storePath)
    day0 = datetime.datetime.fromtimestamp(s.execute("select min(happenedAt) from records where origin!='given'").fetchone()[0]).date()
    fromStore = {}
    for at, retold, asIs in s.execute("select e.happenedAt, e.retold, e.asItHappened from episodes e join records r on r.id=e.recordId where r.origin!='given' order by e.happenedAt"):
        k = (datetime.datetime.fromtimestamp(at).date() - day0).days
        fromStore.setdefault(k, []).append((retold or asIs or "").strip())
    days, sources = [], []
    for k in range(maxDay + 1):
        if k in fromStore:
            days.append(fromStore[k]); sources.append("store"); continue
        lines, pending = [], None
        for speaker, person, text in db.execute("select speaker, person, text from turns where runId=? and dayIndex=? and speaker in ('visitor','sheep') order by id", (rid, k)):
            if speaker == "visitor":
                if pending: lines.append(pending + " and Maya said nothing.")
                pending = f"{person} said '{text.strip()}'"
            elif pending:
                lines.append(pending + (f" and Maya replied '{text.strip()}'." if text.strip() else " and Maya said nothing.")); pending = None
        if pending: lines.append(pending + " and Maya said nothing.")
        days.append(lines); sources.append("turns")
    return days, sources

app = application(root)
processor = serviceConnectModel(repositoryModels(app.database), root).processor(MODEL)
def chat(system, user):
    return (processor.chat(system, user, 0.4, purpose="dayBackground") or "").strip()

def buildRun(rid, kind):
    being = "Maya"
    store, maxDay = META[rid]
    days, sources = episodesByDay(store, rid, min(maxDay, 9))   # the counting lives: up to day 10, the test days are not needed
    print(rid, kind, "sources:", " ".join(f"{k}:{src}" for k, src in enumerate(sources)), flush=True)
    out = {}; before = ""; todays = []
    for k, events in enumerate(days):
        body = "\n".join(f"- {e}" for e in events)
        today = chat(SYS_TODAY.format(B=being), f"The events of the day, oldest first:\n{body}\n\nWhat happened that day:")
        todays.append(today)
        if k == 0:
            before = today
        else:
            before = chat(SYS_BEFORE.format(B=being), f"My account of the days before:\n{before}\n\nAnd then, the day after that:\n{today}\n\nThe last days, older first, in at most 3 sentences:")
        ongoing = chat(SYS_ONGOING.format(B=being), "The last days, older first:\n" + "\n".join(f"day {i + 1}: {t}" for i, t in enumerate(todays)) + "\n\nWhat is going on in my life right now, one sentence:")
        out[k] = {"today": today, "before": before, "ongoing": ongoing, "source": sources[k], "events": events}
        print(rid, kind, "day", k, "|", today[:80].replace("\n", " "), "||", ongoing[:80], flush=True)
    return rid, out

jobs = [(rid, kind) for kind, rids in RUNS.items() for rid in rids]
META = {rid: (db.execute("select storePath from runs where id=?", (rid,)).fetchone()[0],
              db.execute("select max(dayIndex) from turns where runId=?", (rid,)).fetchone()[0]) for rid, _ in jobs}   # read in the main thread
print(len(jobs), "runs", {k: v for k, v in RUNS.items()}, flush=True)
result = {}
with ThreadPoolExecutor(4) as ex:
    for rid, out in ex.map(lambda j: buildRun(*j), jobs):
        result[rid] = out
        json.dump({"runs": RUNS, "days": result}, open(f"{HERE}/days.json", "w"), indent=1, ensure_ascii=False)
print("DONE days.json", flush=True)
