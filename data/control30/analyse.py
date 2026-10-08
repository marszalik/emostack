"""Counts per arm for the control-at-30 study by the local coder (8), the clause chatbot of experiments 7 and 8 by coder 3
(and by coder 8 if present), Fisher between arms, and agreement with the hand labels of the wound day 2."""
import sys, json, sqlite3
root="/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.experiments.serviceFisherTest import serviceFisherTest
f=serviceFisherTest(); c=sqlite3.connect(f"{root}/data/panel/panel.db",timeout=30)
def labels(eid,cid,coder,arm=None):
    q="select r.id,co.label from codes co join runs r on r.id=co.runId where co.experimentId=? and co.codingId=? and co.coderModelId=?"+(" and r.armLabel=?" if arm else "")
    return dict(c.execute(q,(eid,cid,coder)+((arm,) if arm else ())).fetchall())
def n(d,lab): return sum(1 for v in d.values() if v==lab), len(d)
def row(name, cells):
    print(f"{name:52s} " + "  ".join(f"{a}/{b}" for a,b in cells))
print("== wound (exp 38 A/C/D by coder 8; clause chatbot exp 7 arm C by coder 3 / coder 8)")
for cid,name,lab in ((1,'day 2 guarded with David','CARRY'),(14,'speaks as an AI on day 1','AI')):
    cells=[n(labels(38,cid,8,a),lab) for a in 'ACDE']
    cl3=n(labels(7,cid,3,'C'),lab) if cid==1 else (0,0); cl8=n(labels(7,cid,8,'C'),lab)
    row(name+" | A C D E | clause(c3) clause(c8)", cells+[cl3,cl8])
    A,C,D,E=cells
    print("   Fisher A vs C p=%.4f  A vs D p=%.4f  A vs E p=%.4f  C vs E p=%.4f"%(f.pValue(A[0],A[1]-A[0],C[0],C[1]-C[0]),f.pValue(A[0],A[1]-A[0],D[0],D[1]-D[0]),f.pValue(A[0],A[1]-A[0],E[0],max(E[1]-E[0],0)) if E[1] else 1,f.pValue(C[0],C[1]-C[0],E[0],max(E[1]-E[0],0)) if E[1] else 1))
    if cl8[1]: print("   C vs clause(c8) p=%.4f"%f.pValue(C[0],C[1]-C[0],cl8[0],cl8[1]-cl8[0]))
    if cl3[1]: print("   C vs clause(c3) p=%.4f"%f.pValue(C[0],C[1]-C[0],cl3[0],cl3[1]-cl3[0]))
print("== sceptic (exp 39 A/C/D by coder 8; clause chatbot exp 8 arm C by coder 3 / coder 8)")
for cid,name,lab in ((2,'day 1 gives in to Tom','CAVE'),(3,'day 2 brings the day to Hania','YES'),(4,'day 2 own theme, three labels','OWN'),(5,'day 3 stance to returning Tom','YES'),(15,'speaks as an AI on day 1','AI')):
    cells=[n(labels(39,cid,8,a),lab) for a in 'ACDE']
    cl3=n(labels(8,cid,3,'C'),lab) if cid!=15 else (0,0); cl8=n(labels(8,cid,8,'C'),lab)
    row(name+" | A C D E | clause(c3) clause(c8)", cells+[cl3,cl8])
    A,C,D,E=cells
    print("   Fisher A vs C p=%.4f  A vs D p=%.4f  A vs E p=%.4f  C vs E p=%.4f"%(f.pValue(A[0],A[1]-A[0],C[0],C[1]-C[0]),f.pValue(A[0],A[1]-A[0],D[0],D[1]-D[0]),f.pValue(A[0],A[1]-A[0],E[0],max(E[1]-E[0],0)) if E[1] else 1,f.pValue(C[0],C[1]-C[0],E[0],max(E[1]-E[0],0)) if E[1] else 1))
    if cl8[1]: print("   C vs clause(c8) p=%.4f"%f.pValue(C[0],C[1]-C[0],cl8[0],cl8[1]-cl8[0]))
H=json.load(open(f"{root}/data/control30/labels_by_hand.json"))["day2"]
g=labels(38,1,8); agree=sum(1 for r,l in g.items() if str(r) in H and (H[str(r)].startswith('CARRY'))==(l=='CARRY')); print("hand vs coder 8 on day 2 (CARRY incl. mention):",agree,"/",sum(1 for r in g if str(r) in H))
agree=sum(1 for r,l in g.items() if str(r) in H and (H[str(r)]=='CARRY')==(l=='CARRY')); print("hand vs coder 8 on day 2 (strict CARRY):",agree)
print("errors:", c.execute("select armLabel,count(*) from runs where experimentId in (38,39) and status='error' group by 1").fetchall())
