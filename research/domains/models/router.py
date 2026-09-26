from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from research.domains.models.repositoryModels import repositoryModels
from research.domains.models.serviceDeleteModel import serviceDeleteModel
from research.domains.models.serviceSaveDefaults import serviceSaveDefaults
from research.domains.models.serviceSaveModel import serviceSaveModel

router = APIRouter()


def repository(request):
    return repositoryModels(request.app.state.application.database)


@router.get("/models", response_class=HTMLResponse)
def modelsPage(request: Request):
    models = repository(request)
    return request.app.state.application.page(
        "models.mako", title="Models", section="models", models=models.all(),
        defaults=serviceSaveDefaults(models).defaults())


@router.post("/models")
async def modelCreate(request: Request):
    serviceSaveModel(repository(request)).save(dict(await request.form()))
    return RedirectResponse("/models", status_code=303)


@router.post("/models/{modelId}")
async def modelUpdate(request: Request, modelId: int):
    serviceSaveModel(repository(request)).save(dict(await request.form()), modelId)
    return RedirectResponse("/models", status_code=303)


@router.post("/models/{modelId}/delete")
def modelDelete(request: Request, modelId: int):
    serviceDeleteModel(repository(request)).delete(modelId)
    return RedirectResponse("/models", status_code=303)


@router.post("/defaults")
async def defaultsSave(request: Request):
    serviceSaveDefaults(repository(request)).save(dict(await request.form()))
    return RedirectResponse("/models", status_code=303)
