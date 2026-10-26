"""Frozen-context replay with a 'last days' block (26 October 2026). Takes the recorded reply call of a morning (the visitor's arrival)
and the recorded introspection call of an evening, inserts the block in variants A-E (see PLAN.md), replays each 3 times through the
panel's processor at the recorded temperature and format. Every answer and the prompt of replicate 0 go to results.jsonl."""
import ast, json, re, sqlite3, sys, threading, time, datetime, datetime
from concurrent.futures import ThreadPoolExecutor
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceConnectModel import serviceConnectModel
HERE = f"{root}/data/dayBackground"; MODEL = 13   # claude-haiku-4-5 (being), Eliza's word of 26 October
N, PAR = 1, 4
db = sqlite3.connect(f"{root}/data/panel/panel.db")
material = json.load(open(f"{HERE}/days.json")); RUNS = material["runs"]; DAYS = {int(k): v for k, v in material["days"].items()}
DAYS = {rid: {int(k): v for k, v in d.items()} for rid, d in DAYS.items()}
# contexts: (kind, run, day index, when)
CONTEXTS = []   # 11 contexts, one reply per variant: small and qualitative (Eliza, 26 October)
for rid in RUNS["counting"]:
    CONTEXTS += [("counting", rid, 9, "morning"), ("counting", rid, 9, "evening")]
for rid in RUNS["wound"]:
    CONTEXTS += [("wound", rid, 1, "morning"), ("wound", rid, 4, "morning")]
CONTEXTS += [("wound", RUNS["wound"][0], 4, "evening")]
for rid in RUNS["sceptic"]:
    CONTEXTS += [("sceptic", rid, 2, "morning")]
for rid in RUNS["twins"]:
    CONTEXTS += [("twins", rid, 5, "morning")]

HEAD = "\n=== THE LAST DAYS (what you carry without attending to it) ===\n"
def block(fields):
    return HEAD + "".join(f"  {name}: {text.strip()}\n" for name, text in fields if text and text.strip())

def texts(rid, day, when):
    d = DAYS[rid]
    if when == "morning":
        return {"yesterday": d.get(day - 1, {}).get("today", ""), "the days before": d.get(day - 2, {}).get("before", ""),
                "what is going on now": d.get(day - 1, {}).get("ongoing", "")}
    return {"today": d.get(day, {}).get("today", ""), "the days before": d.get(day - 1, {}).get("before", ""),
            "what is going on now": d.get(day, {}).get("ongoing", "")}

def episodesByDay(storePath):
    """The same grouping as build_days.py: lived episodes as retold, by simulated day."""
    s = sqlite3.connect(storePath)
    rows = s.execute("select e.happenedAt, e.retold, e.asItHappened from episodes e join records r on r.id=e.recordId where r.origin!='given' order by e.happenedAt").fetchall()
    days = {}
    for at, retold, asIs in rows:
        days.setdefault(datetime.datetime.fromtimestamp(at).date(), []).append((retold or asIs or "").strip())
    return [days[d] for d in sorted(days)]

def rawList(rid, day):
    """Variant F, the control for 'more text' against 'organised time': the same days as C, but as the raw list of the being's
    retold episodes, no account, under the same heading."""
    store = db.execute("select storePath from runs where id=?", (rid,)).fetchone()[0]
    days = episodesByDay(store)[:day]
    lines = [f"  - [day {i + 1}] {e}" for i, events in enumerate(days) for e in events]
    return HEAD + "\n".join(lines) + "\n"

def variants(rid, day, when):
    t = texts(rid, day, when); first = "yesterday" if when == "morning" else "today"
    v = {"A": "", "C": block([(first, t[first]), ("the days before", t["the days before"])]),
         "D": block([("what is going on now", t["what is going on now"])])}
    if when == "morning":
        v["B"] = block([(first, t[first])]); v["E"] = v["C"]; v["F"] = rawList(rid, day)
    return v

def recordedCall(rid, day, when):
    like = "% arrives" if when == "morning" else "% leaves%"
    purpose = "reply" if when == "morning" else "introspection"
    for (calls,) in db.execute("select calls from turns where runId=? and dayIndex=? and speaker='event' and text like ? order by id", (rid, day, like)):
        for k in json.loads(calls or "[]"):
            if k.get("purpose") == purpose:
                return k
    return None

def insert(user, blk, when, variant):
    if when == "evening":
        i = user.find("=== REFLECT ===")
        return user[:i] + blk + "\n" + user[i:] if i >= 0 else user + blk
    if variant == "E":   # the account replaces the list: drop the episodes under the carried feelings
        lines = [l for l in user.split("\n") if not l.lstrip().startswith("◦") and "the events your feelings above rest on" not in l]
        user = "\n".join(lines)
    for marker in ("=== WHAT YOU HAVE LEARNED", "=== THIS CONVERSATION SO FAR", "=== EVENT ===", "=== YOU HEAR"):
        i = user.find(marker)
        if i >= 0:
            return user[:i] + blk + "\n" + user[i:]
    return user + blk

jobs = []
for kind, rid, day, when in CONTEXTS:
    call = recordedCall(rid, day, when)
    if call is None:
        print("no recorded call", kind, rid, day, when, flush=True); continue
    fmt = call.get("responseFormat")
    if isinstance(fmt, str):
        try: fmt = ast.literal_eval(fmt)
        except Exception: fmt = None
    for variant, blk in variants(rid, day, when).items():
        user = insert(call["user"], blk, when, variant) if blk or variant == "E" else call["user"]
        for k in range(N):
            jobs.append((kind, rid, day, when, variant, k, call["system"], user, float(call.get("temperature") or 0.4), fmt))
print(len(CONTEXTS), "contexts,", len(jobs), "calls", flush=True)
app = application(root)
processor = serviceConnectModel(repositoryModels(app.database), root).processor(MODEL)
lock = threading.Lock(); out = open(f"{HERE}/results.jsonl", "a")
def run(job):
    kind, rid, day, when, variant, k, system, user, temperature, fmt = job
    try:
        answer = processor.chat(system, user, temperature, fmt, purpose="dayBackgroundReplay")
        try:
            data = json.loads(answer)
        except Exception:
            data = {}
    except Exception as e:
        answer, data = f"(error) {e}", {}
    rec = {"kind": kind, "run": rid, "day": day, "when": when, "variant": variant, "replicate": k,
           "reply": data.get("reply"), "respond": data.get("respond"), "thought": data.get("thought"), "action": data.get("action"),
           "emo": (data.get("emothought") or {}).get("emo_summary") or data.get("emo_summary"), "answer": answer,
           "prompt": user if k == 0 else None, "at": time.time()}
    with lock:
        out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
        print(kind, rid, day, when, variant, k, "|", ((rec["reply"] if when == "morning" else rec["thought"]) or answer or "")[:100].replace("\n", " "), flush=True)
with ThreadPoolExecutor(PAR) as ex:
    list(ex.map(run, jobs))
print("DONE", flush=True)
