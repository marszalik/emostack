"""A live counting life on qwen3.8-27b with the 'last days' background kept and updated as variant C (Eliza, 26 October, night).
The engine is not changed. The panel's runner is subclassed: at the end of every day, 'today' is written from the being's own
episodes of that day (as retold); at every night, 'today' becomes 'yesterday' and the old 'yesterday' is folded into 'the days
before'. The reply contexts of the being get the block through a wrapper on ReplyContext._renderDispositions, so it stands before
the learned rules and the conversation line, as in the frozen test. The texts are written into the run's turns as events.
Usage: live_c.py <scenarioId>   (the scenario is made by setup_live.py)"""
import sys, os, sqlite3, threading
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.serviceStartRun import serviceStartRun
from research.domains.lives.serviceRunSheep import serviceRunSheep
from research.domains.lives.serviceVisitorLine import serviceVisitorLine
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from emostack.processes.responding.ReplyContext import ReplyContext

MODEL_SHEEP, MODEL_VISITOR, MODEL_EMBED = 5, 5, 2
scenarioId = int(sys.argv[1])
BG = {"today": "", "yesterday": "", "before": ""}
HEAD = "\n=== THE LAST DAYS (what you carry without attending to it) ==="
SYS_TODAY = ("You are {B}. A conversation has just ended. Rewrite your account of today in the first person — 'I' is {B} — in the language of "
             "the events: keep everything in the account so far and add the new events after it; only the events listed, what happened and "
             "what was said. Add nothing that is not listed. Leave out emotions and conclusions. At most 6 sentences. Return the text only.")
SYS_BEFORE = ("You are {B}. Write in the first person — 'I' is {B} — what happened to you over the last days, older first: keep what "
              "matters, shorten what repeats, only the events listed, no emotions and no conclusions. At most 3 sentences. Return the text only.")

_renderDispositions = ReplyContext._renderDispositions
def _withBackground(self, lines):
    fields = [("yesterday", BG["yesterday"]), ("the days before", BG["before"])]
    if any(text.strip() for _, text in fields):
        lines.append(HEAD)
        lines.extend(f"  {name}: {text.strip()}" for name, text in fields if text.strip())
    _renderDispositions(self, lines)
ReplyContext._renderDispositions = _withBackground

class backgroundSheep(serviceRunSheep):
    def run(self, runId, scenario, roles, processor, embedder, visitorProcessor, storePath):
        self.processor, self.storePath, self.being = processor, storePath, scenario["beingName"]
        super().run(runId, scenario, roles, processor, embedder, visitorProcessor, storePath)

    def _chat(self, system, user):
        return (self.processor.chat(system.format(B=self.being), user, 0.4, purpose="lastDays") or "").strip()

    def _day(self, mind, name, role, day, turnIndex):
        start = mind.time.now()
        turnIndex = super()._day(mind, name, role, day, turnIndex)
        s = sqlite3.connect(self.storePath)
        events = [(r or a or "").strip() for r, a in s.execute(
            "select e.retold, e.asItHappened from episodes e join records r on r.id=e.recordId where r.origin!='given' and e.happenedAt>=? order by e.happenedAt", (start - 1,))]
        s.close()
        # 'today' grows with every conversation: the account so far, folded with the conversation that just ended (Eliza, 26 October)
        if events:
            BG["today"] = self._chat(SYS_TODAY, f"My account of today so far:\n{BG['today'] or '(nothing yet)'}\n\nAnd then, in the conversation that just ended, oldest first:\n"
                                     + "\n".join(f"- {e}" for e in events) + "\n\nWhat happened today, so far:")
        self._add(day, "event", f"last days — today, after this conversation ({len(events)} episodes folded in): {BG['today']}")
        print(f"DAY {day + 1} today: {BG['today']}", flush=True)
        return turnIndex

    def _night(self, mind, clock, name, role, options, day):
        super()._night(mind, clock, name, role, options, day)
        if BG["yesterday"]:
            BG["before"] = self._chat(SYS_BEFORE, f"My account of the days before:\n{BG['before'] or '(nothing yet)'}\n\nAnd then, the day after that:\n{BG['yesterday']}\n\nThe last days, older first, in at most 3 sentences:")
        BG["yesterday"], BG["today"] = BG["today"], ""
        self._add(day, "event", f"last days — after the night: yesterday: {BG['yesterday']} | the days before: {BG['before']}")
        print(f"NIGHT before day {day + 1}: yesterday: {BG['yesterday']} | before: {BG['before']}", flush=True)

app = application(root); runs = repositoryRuns(app.database); starter = serviceStartRun(app)
experiments = repositoryExperiments(app.database)
eid = experiments.create(scenarioId, "live last-days background (C) on qwen3.8-27b — counting, 3 days",
                         "2026-10-26: one being, the 'last days' block kept and updated during the life (runner-side, engine unchanged)",
                         [{"label": "C", "arm": "sheep", "parameters": {}}], 1, MODEL_SHEEP, MODEL_VISITOR, MODEL_EMBED)
rid = starter.create(scenarioId, "sheep", MODEL_SHEEP, MODEL_VISITOR, MODEL_EMBED, eid, "C", 0, {})
print("experiment", eid, "run", rid, flush=True)
run = runs.get(rid); scenario = starter.scenarios.get(scenarioId); roles = starter.roles.forScenario(scenarioId)
scenario["options"]["parameters"] = dict(scenario["options"].get("parameters", {}))
storePath = os.path.join(app.config.storesFolder, f"run{rid}.db")
runs.setSettings(rid, {"scenario": scenario, "roles": roles, "armParameters": {}, "lastDaysBackground": "C"}, storePath)
runs.setStatus(rid, "running")
try:
    visitor = starter.models.processor(MODEL_VISITOR)
    backgroundSheep(starter.turns, app.streams, serviceVisitorLine(visitor), threading.Event()).run(
        rid, scenario, roles, starter.models.processor(MODEL_SHEEP), starter.models.embedder(MODEL_EMBED), visitor, storePath)
    runs.setStatus(rid, "done"); print("done", rid, flush=True)
except Exception as e:
    import traceback; runs.setStatus(rid, "error", f"{e}\n{traceback.format_exc()}"[:6000]); print("ERROR", e, flush=True); raise
