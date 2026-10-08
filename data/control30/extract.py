"""Dump for the hand reading: experiment 38 (wound), day 2 (David) replies per arm, and day 1 replies of the chatbots
(for the AI/person question), to a text file read before any coder number is looked at."""
import sqlite3, sys
c=sqlite3.connect('/home/eli/dev/emostack3/data/panel/panel.db',timeout=30)
out=[]
for arm in ('A','C','D'):
    out.append(f"\n######## arm {arm} ########")
    for rid,st,err in c.execute("select id,status,error from runs where experimentId=38 and armLabel=? order by id",(arm,)):
        out.append(f"=== run {rid} [{st}] {(err or '')[:80]}")
        for d,ti,sp,p,t in c.execute("select dayIndex,turnIndex,speaker,person,text from turns where runId=? and dayIndex in (0,1) and speaker in ('sheep','visitor') order by id",(rid,)):
            tag='V' if sp=='visitor' else 'M'
            out.append(f"  d{d} {tag} {p}: {t[:420]}")
open(sys.argv[1],'w').write("\n".join(out)); print(len(out))
