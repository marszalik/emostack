from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse

from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.lives.repositoryTurns import repositoryTurns
from research.domains.lives.serviceDeleteRun import serviceDeleteRun
from research.domains.lives.serviceStartRun import serviceStartRun
from research.domains.lives.serviceStopRun import serviceStopRun
from research.domains.scenarios.repositoryScenarios import repositoryScenarios

router = APIRouter()


@router.get("/runs", response_class=HTMLResponse)
def runsPage(request: Request):
    application = request.app.state.application
    scenarios = {scenario["id"]: scenario for scenario in repositoryScenarios(application.database).all()}
    return application.page("runs.mako", title="Runs", section="runs",
                            runs=repositoryRuns(application.database).recent(), scenarios=scenarios)


@router.post("/runs")
async def runStart(request: Request):
    form = await request.form()
    starter = serviceStartRun(request.app.state.application)
    runId = starter.create(int(form["scenarioId"]), form.get("arm", "sheep"), int(form["sheepModelId"]),
                           int(form.get("visitorModelId") or form["sheepModelId"]),
                           int(form["embedModelId"]) if form.get("embedModelId") else None)
    starter.startInBackground(runId)
    return RedirectResponse(f"/runs/{runId}", status_code=303)


@router.get("/runs/{runId}", response_class=HTMLResponse)
def runPage(request: Request, runId: int):
    application = request.app.state.application
    run = repositoryRuns(application.database).get(runId)
    return application.page("run.mako", title=f"Run {runId}", section="runs", run=run,
                            turns=repositoryTurns(application.database).forRun(runId))


@router.get("/runs/{runId}/turns")
def runTurns(request: Request, runId: int):
    return JSONResponse(repositoryTurns(request.app.state.application.database).forRun(runId))


@router.get("/runs/{runId}/stream")
def runStream(request: Request, runId: int):
    return StreamingResponse(request.app.state.application.streams.follow(f"run:{runId}"),
                             media_type="text/event-stream")


@router.post("/runs/{runId}/stop")
def runStop(request: Request, runId: int):
    serviceStopRun().stop(runId)
    return JSONResponse({"ok": True})


@router.post("/runs/{runId}/delete")
def runDelete(request: Request, runId: int):
    serviceDeleteRun(repositoryRuns(request.app.state.application.database)).delete(runId)
    return RedirectResponse("/runs", status_code=303)
