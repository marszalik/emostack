#!/bin/bash
# Watchdog v2: every 2 min a REAL completion (60 s). Two failures in a row -> stop pool, sleep+wake the card,
# start vLLM, reset running runs, restart pool on what is queued. The card hangs with /v1/models still answering.
export XDG_RUNTIME_DIR=/run/user/$(id -u) DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
cd /home/eli/dev/emostack3
D=data/control30; LOG=$D/watchdog.log; fails=0
log(){ echo "$(date '+%H:%M:%S') $*" >> $LOG; }
gen_ok(){ curl -s -m 60 -H "Authorization: Bearer ElizaJestPiekna" -H "Content-Type: application/json" -d '{"model":"qwen3.8-27b","messages":[{"role":"user","content":"Say OK."}],"max_tokens":3,"chat_template_kwargs":{"enable_thinking":false}}' http://127.0.0.1:4000/v1/chat/completions | grep -q '"content"'; }
log "watchdog v2 start"
while true; do
  left=$(python3 -c "import sqlite3;c=sqlite3.connect('data/panel/panel.db',timeout=30);print(c.execute(\"select count(*) from runs where experimentId in (38,39) and status in ('queued','running')\").fetchone()[0])")
  if [ "$left" = "0" ]; then log "battery finished"; break; fi
  if gen_ok; then fails=0; else fails=$((fails+1)); log "generation failed ($fails) | $(gpu stan 2>&1 | grep -i 'obudowa\|temperatura' | tr '\n' ' ')"; fi
  if [ $fails -ge 2 ]; then
    log "RECOVERY: stop pool and runs"; touch $D/STOP; for p in $(ps -eo pid,args | grep "[r]unOne.py\|[c]ontrol30/pool.py\|[w]ill/pool.py\|[c]li.ts serve" | awk '{print $1}'); do kill $p; done; sleep 3
    log "spij: $(timeout 180 gpu spij 2>&1 | tail -1)"; sleep 10
    log "budz: $(timeout 240 gpu budz 2>&1 | tail -1)"; sleep 5
    log "tekst: $(timeout 120 gpu tekst 2>&1 | tail -1)"
    for i in $(seq 1 40); do sleep 15; gen_ok && break; done
    if gen_ok; then
      log "generation back after $((i*15))s"
      python3 - <<'PY' >> $LOG 2>&1
import sqlite3, os
c=sqlite3.connect('data/panel/panel.db', timeout=30)
for rid,store in c.execute("select id,storePath from runs where experimentId in (38,39) and status in ('running','error')").fetchall():
    c.execute("delete from turns where runId=?",(rid,)); c.execute("update runs set status='queued', error='' where id=?",(rid,))
    if store and os.path.exists(store): os.remove(store)
    print('reset run', rid)
c.commit()
ids=[str(r) for (r,) in c.execute("select id from runs where experimentId in (38,39) and status='queued' order by id")]
open('data/control30/battery_resume.txt','w').write(' '.join(ids)); print('queued', len(ids))
PY
      rm -f $D/STOP; (setsid nohup .venv/bin/python $D/pool.py battery_resume.txt >> $D/pool_resume.log 2>&1 < /dev/null &); log "pool restarted"; fails=0
    else
      log "generation still dead after 10 min; retry next cycle"; rm -f $D/STOP; fails=1
    fi
  fi
  sleep 120
done
