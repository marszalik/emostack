"""Run the ids in run_ids.txt in parallel, width read from maxpar.txt before each start; a STOP file stops new starts."""
import os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ids = open(os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "run_ids.txt")).read().split()
python = "/home/eli/dev/emostack3/.venv/bin/python"
import sqlite3
panel = sqlite3.connect("/home/eli/dev/emostack3/data/panel/panel.db", timeout=30)
def queued(rid):
    row = panel.execute("select status from runs where id = ?", (int(rid),)).fetchone()
    return bool(row) and row[0] == "queued"
running = []
for rid in ids:
    if not queued(rid):
        continue
    while True:
        running = [p for p in running if p.poll() is None]
        if os.path.exists(os.path.join(HERE, "STOP")): break
        if len(running) < int(open(os.path.join(HERE, "maxpar.txt")).read().strip() or 1): break
        time.sleep(3)
    if os.path.exists(os.path.join(HERE, "STOP")):
        print("STOP", flush=True); break
    log = open(os.path.join(HERE, "logs", f"run{rid}.log"), "w")
    running.append(subprocess.Popen([python, os.path.join(HERE, "runOne.py"), rid], stdout=log, stderr=subprocess.STDOUT))
    print(f"started {rid} at {time.strftime('%H:%M:%S')}", flush=True); time.sleep(2)
for p in running: p.wait()
print("ALL DONE", flush=True)
