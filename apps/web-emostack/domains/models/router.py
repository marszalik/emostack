from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from domains.auth.serviceWhoIsThis import serviceWhoIsThis
from domains.models.Provider import Provider
from domains.models.Purpose import Purpose
from domains.models.repositoryPersonalModels import repositoryPersonalModels
from domains.models.serviceConnect import serviceConnect
from domains.models.serviceDeletePersonalModel import serviceDeletePersonalModel
from domains.models.serviceSavePersonalModel import serviceSavePersonalModel
from domains.models.serviceTestPersonalModel import serviceTestPersonalModel

router = APIRouter()


def signedIn(request):
    person = serviceWhoIsThis(request.app.state.application).person(request)
    if person is None:
        raise HTTPException(401, "sign in first")
    return person


def masked(model):
    if not model:
        return None
    key = model["apiKey"]
    shown = {name: value for name, value in model.items() if name != "apiKey"}
    shown["keyMasked"] = f"{key[:6]}…{key[-4:]}" if len(key) > 12 else "•" * len(key)
    shown["routes"] = {purpose: {name: value for name, value in route.items() if name != "apiKey"}
                       for purpose, route in model.get("routes", {}).items()}
    return shown


@router.get("/me/model", response_class=HTMLResponse)
def myModelPage(request: Request, reason: str = ""):
    person = signedIn(request)
    application = request.app.state.application
    return application.page("myModel.mako", section="myModel", user=person.toDict(), level=person.level,
                            providers=[provider.toDict() for provider in Provider.all()], purposes=Purpose.all(),
                            saved=masked(repositoryPersonalModels(application.database).get(person.email)),
                            reason=reason)


@router.post("/me/model")
async def myModelSave(request: Request):
    person = signedIn(request)
    try:
        model = serviceSavePersonalModel(repositoryPersonalModels(request.app.state.application.database)).save(
            person.email, dict(await request.form()))
    except ValueError as error:
        return JSONResponse({"ok": False, "error": str(error)}, status_code=400)
    return {"ok": True, "saved": masked(model)}


@router.post("/me/model/test")
async def myModelTest(request: Request):
    person = signedIn(request)
    application = request.app.state.application
    try:
        model = serviceSavePersonalModel(repositoryPersonalModels(application.database)).build(
            person.email, dict(await request.form()))
    except ValueError as error:
        return JSONResponse({"ok": False, "message": str(error)}, status_code=400)
    ok, message = serviceTestPersonalModel(serviceConnect(application), application.config.serverEmbedder).test(model)
    return {"ok": ok, "message": message}


@router.post("/me/model/delete")
def myModelDelete(request: Request):
    person = signedIn(request)
    serviceDeletePersonalModel(repositoryPersonalModels(request.app.state.application.database)).delete(person.email)
    return {"ok": True}
