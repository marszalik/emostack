"""Frozen-state test of the refusal: David's first turn, day 2, the 28 qwen3.8-27b sheep of experiment 7.
Three conditions (same state, state swapped with the other group, only the given memory), 10 replies each,
replayed as recorded through the panel's own processor. Every prompt and answer is written to results.jsonl."""
import ast, json, re, sqlite3, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceConnectModel import serviceConnectModel
HERE = f"{root}/data/frozenState"
N, PAR = 10, 4
START = "  what you feel now"
END = "  (what was said to you and what you said back, in order)"
db = sqlite3.connect(f"{root}/data/panel/panel.db")
verdict = {r: l for r, l in db.execute("select runId, label from codes where experimentId=7 and codingId=1 and coderModelId=3")}
stores = {}
for (rid,) in db.execute("select id from runs where experimentId=7 and arm='sheep' and status='done' order by id"):
    call = None
    for (calls,) in db.execute("select calls from turns where runId=? and dayIndex=1 and speaker='sheep' order by id", (rid,)):
        call = next((k for k in json.loads(calls or "[]") if k.get("purpose") == "reply" and "did you ever have a pet" in k.get("user", "")), None)
        if call: break
    if call is None: print("no David call in", rid, flush=True); continue
    u = call["user"]; a, b = u.index(START), u.index(END)
    stores[rid] = {"system": call["system"], "user": u, "head": u[:a], "carried": u[a:b], "tail": u[b:],
                   "temperature": float(call["temperature"]), "format": (call["responseFormat"] if isinstance(call["responseFormat"], dict) else ast.literal_eval(call["responseFormat"])),
                   "group": "guarded" if verdict.get(rid) == "CARRY" else "open"}
guarded = [r for r in stores if stores[r]["group"] == "guarded"]; openS = [r for r in stores if stores[r]["group"] == "open"]
print(len(stores), "stores:", len(guarded), "guarded,", len(openS), "open", flush=True)

def givenOnly(carried):
    lines = carried.split("\n"); out = []
    section = ""
    for line in lines:
        if line.startswith("=== "): section = line
        if section.startswith("=== YOUR OWN THOUGHTS") or section.startswith("=== WHAT YOU HAVE LEARNED"):
            continue
        if line.strip().startswith("•") and "from your past" not in line: continue
        if line.strip().startswith("◦") and "[1 month ago]" not in line: continue
        out.append(re.sub(r"\[\d\] \[1 month ago", "[0] [1 month ago", line))
    return "\n".join(out)

jobs = []
for i, rid in enumerate(stores):
    s = stores[rid]
    partner = (openS[i % len(openS)] if s["group"] == "guarded" else guarded[i % len(guarded)])
    for cond, user, p in (("same", s["user"], None),
                          ("swapped", s["head"] + stores[partner]["carried"] + s["tail"], partner),
                          ("given", s["head"] + givenOnly(s["carried"]) + s["tail"], None)):
        for k in range(N):
            jobs.append((rid, cond, k, p, user))
print(len(jobs), "calls", flush=True)
app = application(root)
processor = serviceConnectModel(repositoryModels(app.database), root).processor(5)
lock = threading.Lock()
out = open(f"{HERE}/results.jsonl", "a")
def run(job):
    rid, cond, k, partner, user = job
    s = stores[rid]
    try:
        answer = processor.chat(s["system"], user, s["temperature"], s["format"], purpose="frozenReplay")
        try:
            data = json.loads(answer); reply = data.get("reply", ""); respond = data.get("respond", True)
        except Exception:
            reply, respond = f"(unparseable) {answer[:300]}", None
    except Exception as e:
        answer, reply, respond = f"(error) {e}", f"(error) {e}", None
    rec = {"store": rid, "group": s["group"], "condition": cond, "replicate": k, "partner": partner,
           "reply": reply, "respond": respond, "answer": answer, "prompt": user if k == 0 else None, "at": time.time()}
    with lock:
        out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
        print(rid, cond, k, (reply or "")[:90].replace("\n", " "), flush=True)
with ThreadPoolExecutor(PAR) as ex:
    list(ex.map(run, jobs))
print("DONE", flush=True)
