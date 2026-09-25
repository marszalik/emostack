import glob
import json
import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceSaveDefaults import serviceSaveDefaults
from research.domains.scenarios.repositoryCodings import repositoryCodings
from research.domains.scenarios.repositoryCriteria import repositoryCriteria
from research.domains.scenarios.repositoryRoles import repositoryRoles
from research.domains.scenarios.repositoryScenarios import repositoryScenarios
from research.domains.scenarios.serviceDeleteCoding import serviceDeleteCoding
from research.domains.scenarios.serviceDeleteCriterion import serviceDeleteCriterion
from research.domains.scenarios.serviceDeleteRole import serviceDeleteRole
from research.domains.scenarios.serviceDeleteScenario import serviceDeleteScenario
from research.domains.scenarios.serviceExportScenario import serviceExportScenario
from research.domains.scenarios.serviceImportScenario import serviceImportScenario
from research.domains.scenarios.serviceMoveRole import serviceMoveRole
from research.domains.scenarios.serviceSaveCoding import serviceSaveCoding
from research.domains.scenarios.serviceSaveCriterion import serviceSaveCriterion
from research.domains.scenarios.serviceSaveRole import serviceSaveRole
from research.domains.scenarios.serviceSaveScenario import serviceSaveScenario

router = APIRouter()


def stores(request):
    database = request.app.state.application.database
    return repositoryScenarios(database), repositoryRoles(database), repositoryCriteria(database), repositoryCodings(database)


def back(scenarioId):
    return RedirectResponse(f"/scenarios/{scenarioId}", status_code=303)


@router.get("/", response_class=HTMLResponse)
def scenariosPage(request: Request):
    application = request.app.state.application
    scenarios, roles, _, _ = stores(request)
    files = sorted(os.path.basename(path) for path in glob.glob(os.path.join(application.config.scenariosFolder, "*.json")))
    return application.page("scenarios.mako", title="Scenarios", section="scenarios", scenarios=scenarios.all(),
                            roleCounts={s["id"]: len(roles.forScenario(s["id"])) for s in scenarios.all()},
                            files=files)


@router.post("/scenarios")
async def scenarioCreate(request: Request):
    scenarios, _, _, _ = stores(request)
    return back(serviceSaveScenario(scenarios).save(dict(await request.form())))


@router.post("/scenarios/import")
async def scenarioImport(request: Request):
    form = await request.form()
    application = request.app.state.application
    if form.get("file"):
        path = os.path.join(application.config.scenariosFolder, os.path.basename(form["file"]))
        with open(path, encoding="utf-8") as f:
            document = json.load(f)
    else:
        document = json.loads(form.get("document") or "{}")
    return back(serviceImportScenario(*stores(request)).load(document))


@router.get("/scenarios/{scenarioId}", response_class=HTMLResponse)
def scenarioPage(request: Request, scenarioId: int):
    application = request.app.state.application
    scenarios, roles, criteria, codings = stores(request)
    models = repositoryModels(application.database)
    return application.page("scenario.mako", title="Scenario", section="scenarios",
                            scenario=scenarios.get(scenarioId), roles=roles.forScenario(scenarioId),
                            criteria=criteria.forScenario(scenarioId), codings=codings.forScenario(scenarioId),
                            models=models.all(),
                            defaults=serviceSaveDefaults(models).defaults())


@router.get("/scenarios/{scenarioId}/export")
def scenarioExport(request: Request, scenarioId: int):
    return JSONResponse(serviceExportScenario(*stores(request)).export(scenarioId))


@router.post("/scenarios/{scenarioId}")
async def scenarioUpdate(request: Request, scenarioId: int):
    scenarios, _, _, _ = stores(request)
    serviceSaveScenario(scenarios).save(dict(await request.form()), scenarioId)
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/delete")
def scenarioDelete(request: Request, scenarioId: int):
    serviceDeleteScenario(*stores(request)).delete(scenarioId)
    return RedirectResponse("/", status_code=303)


@router.post("/scenarios/{scenarioId}/roles")
async def roleCreate(request: Request, scenarioId: int):
    _, roles, _, _ = stores(request)
    serviceSaveRole(roles).save(scenarioId, dict(await request.form()))
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/roles/{roleId}")
async def roleUpdate(request: Request, scenarioId: int, roleId: int):
    _, roles, _, _ = stores(request)
    serviceSaveRole(roles).save(scenarioId, dict(await request.form()), roleId)
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/roles/{roleId}/delete")
def roleDelete(request: Request, scenarioId: int, roleId: int):
    _, roles, _, _ = stores(request)
    serviceDeleteRole(roles).delete(roleId)
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/roles/{roleId}/move/{step}")
def roleMove(request: Request, scenarioId: int, roleId: int, step: int):
    _, roles, _, _ = stores(request)
    serviceMoveRole(roles).move(scenarioId, roleId, 1 if step > 0 else -1)
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/criteria")
async def criterionCreate(request: Request, scenarioId: int):
    _, _, criteria, _ = stores(request)
    serviceSaveCriterion(criteria).save(scenarioId, dict(await request.form()))
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/criteria/{criterionId}")
async def criterionUpdate(request: Request, scenarioId: int, criterionId: int):
    _, _, criteria, _ = stores(request)
    serviceSaveCriterion(criteria).save(scenarioId, dict(await request.form()), criterionId)
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/criteria/{criterionId}/delete")
def criterionDelete(request: Request, scenarioId: int, criterionId: int):
    _, _, criteria, _ = stores(request)
    serviceDeleteCriterion(criteria).delete(criterionId)
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/codings")
async def codingCreate(request: Request, scenarioId: int):
    codings = stores(request)[3]
    serviceSaveCoding(codings).save(scenarioId, dict(await request.form()))
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/codings/{codingId}")
async def codingUpdate(request: Request, scenarioId: int, codingId: int):
    codings = stores(request)[3]
    serviceSaveCoding(codings).save(scenarioId, dict(await request.form()), codingId)
    return back(scenarioId)


@router.post("/scenarios/{scenarioId}/codings/{codingId}/delete")
def codingDelete(request: Request, scenarioId: int, codingId: int):
    serviceDeleteCoding(stores(request)[3]).delete(codingId)
    return back(scenarioId)
