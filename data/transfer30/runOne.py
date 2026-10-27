"""Run one queued life of the research panel in its own process, through the panel's own starter."""
import sys, time
root = "/home/eli/dev/emostack3"; sys.path.insert(0, root)
from research.domains.core.application import application
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.serviceStartRun import serviceStartRun
runId = int(sys.argv[1]); started = time.time()
app = application(root)
serviceStartRun(app).run(runId)
run = repositoryRuns(app.database).get(runId)
print(f"RUN {runId} {run['arm']} {run['status']} in {time.time() - started:.0f}s {(run.get('error') or '')[:200]}", flush=True)
