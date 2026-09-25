from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse

from research.domains.experiments.repositoryCodes import repositoryCodes
from research.domains.experiments.repositoryExperiments import repositoryExperiments
from research.domains.experiments.serviceCodeBlind import serviceCodeBlind
from research.domains.experiments.serviceCodingResults import serviceCodingResults
from research.domains.experiments.serviceCreateExperiment import serviceCreateExperiment
from research.domains.experiments.serviceDeleteExperiment import serviceDeleteExperiment
from research.domains.experiments.serviceExperimentResults import serviceExperimentResults
from research.domains.experiments.serviceJudgeExperiment import serviceJudgeExperiment
from research.domains.experiments.serviceRunExperiment import serviceRunExperiment
from research.domains.experiments.serviceStopExperiment import serviceStopExperiment
from research.domains.judging.repositoryJudges import repositoryJudges
from research.domains.judging.repositoryScores import repositoryScores
from research.domains.lives.repositoryRuns import repositoryRuns
from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceSaveDefaults import serviceSaveDefaults
from research.domains.scenarios.repositoryCodings import repositoryCodings
from research.domains.scenarios.repositoryCriteria import repositoryCriteria
from research.domains.scenarios.repositoryScenarios import repositoryScenarios

router = APIRouter()


@router.get("/experiments", response_class=HTMLResponse)
def experimentsPage(request: Request, scenarioId: int = 0):
    application = request.app.state.application
    database = application.database
    models = repositoryModels(database)
    return application.page("experiments.mako", title="Experiments", section="experiments",
                            experiments=repositoryExperiments(database).all(),
                            scenarios=repositoryScenarios(database).all(), models=models.all(),
                            defaults=serviceSaveDefaults(models).defaults(), chosenScenario=scenarioId)


@router.post("/experiments")
async def experimentCreate(request: Request):
    application = request.app.state.application
    experimentId = serviceCreateExperiment(application).create(dict(await request.form()))
    serviceRunExperiment(application).startInBackground(experimentId)
    return RedirectResponse(f"/experiments/{experimentId}", status_code=303)


@router.get("/experiments/{experimentId}", response_class=HTMLResponse)
def experimentPage(request: Request, experimentId: int):
    application = request.app.state.application
    database = application.database
    experiment = repositoryExperiments(database).get(experimentId)
    runs = repositoryRuns(database)
    results = serviceExperimentResults(runs, repositoryScores(database), repositoryJudges(database),
                                       repositoryCriteria(database)).results(experiment)
    return application.page("experiment.mako", title=f"Experiment {experimentId}", section="experiments",
                            experiment=experiment, runs=runs.forExperiment(experimentId),
                            scenario=repositoryScenarios(database).get(experiment["scenarioId"]),
                            judges=repositoryJudges(database).all(), results=results,
                            codings=repositoryCodings(database).forScenario(experiment["scenarioId"]),
                            coders=[model for model in repositoryModels(database).all() if model["kind"] == "chat"],
                            codingResults=serviceCodingResults(runs, repositoryCodes(database), repositoryCodings(database),
                                                               repositoryModels(database)).results(experiment))


@router.get("/experiments/{experimentId}/stream")
def experimentStream(request: Request, experimentId: int):
    return StreamingResponse(request.app.state.application.streams.follow(f"experiment:{experimentId}"),
                             media_type="text/event-stream")


@router.post("/experiments/{experimentId}/judge")
async def experimentJudge(request: Request, experimentId: int):
    application = request.app.state.application
    form = await request.form()
    experiment = repositoryExperiments(application.database).get(experimentId)
    serviceJudgeExperiment(application).startInBackground(experiment, [int(v) for v in form.getlist("judgeId")])
    return RedirectResponse(f"/experiments/{experimentId}", status_code=303)


@router.post("/experiments/{experimentId}/stop")
def experimentStop(request: Request, experimentId: int):
    serviceStopExperiment(repositoryRuns(request.app.state.application.database)).stop(experimentId)
    return JSONResponse({"ok": True})


@router.post("/experiments/{experimentId}/delete")
def experimentDelete(request: Request, experimentId: int):
    database = request.app.state.application.database
    serviceDeleteExperiment(repositoryExperiments(database), repositoryRuns(database)).delete(experimentId)
    return RedirectResponse("/experiments", status_code=303)


@router.post("/experiments/{experimentId}/code")
async def experimentCode(request: Request, experimentId: int):
    application = request.app.state.application
    form = await request.form()
    experiment = repositoryExperiments(application.database).get(experimentId)
    serviceCodeBlind(application).startInBackground(experiment, int(form["coderModelId"]),
                                                    [int(v) for v in form.getlist("codingId")])
    return RedirectResponse(f"/experiments/{experimentId}", status_code=303)
