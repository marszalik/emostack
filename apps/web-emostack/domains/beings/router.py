from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from domains.auth.serviceWhoIsThis import serviceWhoIsThis
from domains.beings.repositorySnapshots import repositorySnapshots
from domains.beings.serviceBeingMemory import serviceBeingMemory
from domains.beings.serviceCreateBeing import serviceCreateBeing
from domains.beings.serviceDeleteBeing import serviceDeleteBeing
from domains.beings.serviceEngineFor import serviceEngineFor
from domains.beings.serviceListBeings import serviceListBeings
from domains.beings.serviceTakeSnapshot import serviceTakeSnapshot
from domains.beings.serviceWakefulness import serviceWakefulness
from domains.models.serviceConnect import serviceConnect

router = APIRouter()


def signedIn(request):
    person = serviceWhoIsThis(request.app.state.application).person(request)
    if person is None:
        raise HTTPException(401, "sign in first")
    return person


def failing(action):
    try:
        return action()
    except ValueError as error:
        raise HTTPException(400, str(error))


@router.get("/", response_class=HTMLResponse)
def homePage(request: Request):
    application = request.app.state.application
    person = signedIn(request)
    engine = serviceEngineFor(application).reader(person)
    try:
        beings = serviceListBeings(engine).list()
    finally:
        engine.close()
    return application.page(
        "home.mako", section="home", user=person.toDict(), level=person.level, beings=beings,
        snapshots=[] if person.isAdministrator() else repositorySnapshots(application.config.dataFolder).all(),
        needsModel=(application.config.requireUserModel and not serviceConnect(application).hasModel(person)),
        most=application.config.maxBeingsPerPerson)


@router.get("/beings")
def beingsData(request: Request):
    person = signedIn(request)
    engine = serviceEngineFor(request.app.state.application).reader(person)
    try:
        return JSONResponse(serviceListBeings(engine).list())
    finally:
        engine.close()


@router.post("/beings")
async def beingCreate(request: Request):
    application = request.app.state.application
    person = signedIn(request)
    form = dict(await request.form())
    engine = serviceEngineFor(application).reader(person)
    try:
        being = failing(lambda: serviceCreateBeing(engine, application.config.maxBeingsPerPerson).create(person, form))
        return {"ok": True, "id": being.id}
    finally:
        engine.close()


@router.post("/beings/copy/{slug}")
def beingCopy(request: Request, slug: str):
    application = request.app.state.application
    person = signedIn(request)
    engine = serviceEngineFor(application).reader(person)
    try:
        being = failing(lambda: serviceTakeSnapshot(engine, repositorySnapshots(application.config.dataFolder),
                                                    application.config.maxBeingsPerPerson).take(person, slug))
        return {"ok": True, "id": being.id}
    finally:
        engine.close()


@router.post("/beings/{beingId}/delete")
def beingDelete(request: Request, beingId: int):
    person = signedIn(request)
    engine = serviceEngineFor(request.app.state.application).reader(person)
    try:
        failing(lambda: serviceDeleteBeing(engine).delete(beingId))
        return {"ok": True}
    finally:
        engine.close()


@router.post("/beings/{beingId}/awake/{state}")
def beingWakefulness(request: Request, beingId: int, state: int):
    person = signedIn(request)
    engine = serviceEngineFor(request.app.state.application).reader(person)
    try:
        return {"awake": failing(lambda: serviceWakefulness(engine).set(beingId, bool(state)))}
    finally:
        engine.close()


@router.get("/beings/{beingId}", response_class=HTMLResponse)
def beingPage(request: Request, beingId: int):
    application = request.app.state.application
    person = signedIn(request)
    engine = serviceEngineFor(application).reader(person)
    try:
        memory = failing(lambda: serviceBeingMemory(engine).read(beingId))
    finally:
        engine.close()
    return application.page("being.mako", section="home", user=person.toDict(), level=person.level, **memory)
