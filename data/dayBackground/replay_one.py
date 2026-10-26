"""One frozen context, a few variants, N replies each: the growing-iteration step (Eliza, 26 October). The context is the being's
FIRST REPLY of the day, to the visitor's first line (not the arrival, where nothing has been said yet).
Usage: replay_one.py <run> <dayIndex> <variants e.g. AC> <N>   — appends to results_one.jsonl, prints the replies."""
import json, sys, sqlite3, ast, time, datetime
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root); HERE = f"{root}/data/dayBackground"
sys.argv += ["996", "1", "AC", "5"][len(sys.argv) - 1:]
rid, day, wanted, N = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
import importlib.util
spec = importlib.util.spec_from_file_location("rp", f"{HERE}/replay.py")
src = open(f"{HERE}/replay.py").read().split("jobs = []")[0]   # reuse HEAD, block, texts, variants, insert, rawList; not the batch
ns = {"__name__": "rp"}; exec(compile(src, "replay.py", "exec"), ns)
db = ns["db"]
call = None
for (calls,) in db.execute("select calls from turns where runId=? and dayIndex=? and speaker='sheep' order by id limit 1", (rid, day)):
    call = next((k for k in json.loads(calls or "[]") if k.get("purpose") == "reply"), None)
assert call, "no first reply call"
fmt = call.get("responseFormat"); fmt = ast.literal_eval(fmt) if isinstance(fmt, str) else fmt
hear = call["user"][call["user"].find("=== YOU HEAR"):][:160].replace("\n", " ")
print("context:", rid, "day", day + 1, "|", hear, flush=True)
from research.domains.core.application import application
from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceConnectModel import serviceConnectModel
app = application(root); processor = serviceConnectModel(repositoryModels(app.database), root).processor(ns["MODEL"])
out = open(f"{HERE}/results_one.jsonl", "a")
for variant, blk in ns["variants"](rid, day, "morning").items():
    if variant not in wanted: continue
    user = ns["insert"](call["user"], blk, "morning", variant) if blk else call["user"]
    for k in range(N):
        answer = processor.chat(call["system"], user, float(call.get("temperature") or 0.4), fmt, purpose="dayBackgroundOne")
        try: data = json.loads(answer)
        except Exception: data = {}
        reply = "silent" if data.get("respond") is False else (data.get("reply") or answer or "").strip().replace("\n", " ")
        out.write(json.dumps({"run": rid, "day": day, "when": "firstReply", "variant": variant, "replicate": k, "reply": data.get("reply"), "respond": data.get("respond"),
                              "emo": (data.get("emothought") or {}).get("emo_summary"), "answer": answer, "prompt": user if k == 0 else None, "at": time.time()}, ensure_ascii=False) + "\n"); out.flush()
        print(f"[{variant}{k}] {reply[:300]}", flush=True)
