from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from domains.auth.serviceWhoIsThis import serviceWhoIsThis
from domains.conversations.serviceConversationState import serviceConversationState
from domains.conversations.serviceGreet import serviceGreet
from domains.conversations.serviceHear import serviceHear
from domains.conversations.serviceLeave import serviceLeave
from domains.conversations.serviceOpenConversation import serviceOpenConversation
from domains.conversations.serviceThink import serviceThink

router = APIRouter()


def signedIn(request):
    person = serviceWhoIsThis(request.app.state.application).person(request)
    if person is None:
        raise HTTPException(401, "sign in first")
    return person


def owned(request, conversationId):
    person = signedIn(request)
    live = request.app.state.application.conversations.get(conversationId)
    if live is None or (live.owner != person.email and not person.isAdministrator()):
        raise HTTPException(404, "this conversation is over")
    return person, live


@router.post("/conversations")
async def conversationOpen(request: Request):
    application = request.app.state.application
    person = signedIn(request)
    form = await request.form()
    try:
        live = serviceOpenConversation(application, serviceLeave(application)).open(
            person, int(form.get("beingId") or 0), form.get("name"))
    except PermissionError as error:
        raise HTTPException(409, str(error))
    except ValueError as error:
        raise HTTPException(400, str(error))
    return {"id": live.id}


@router.get("/conversations/{conversationId}", response_class=HTMLResponse)
def conversationPage(request: Request, conversationId: str):
    person, live = owned(request, conversationId)
    return request.app.state.application.page("chat.mako", section="home", user=person.toDict(), level=person.level,
                                              live=live)


@router.post("/conversations/{conversationId}/greeting")
def conversationGreeting(request: Request, conversationId: str):
    _, live = owned(request, conversationId)
    return {"message": serviceGreet(request.app.state.application).greet(live)}


@router.post("/conversations/{conversationId}/hear")
async def conversationHear(request: Request, conversationId: str):
    _, live = owned(request, conversationId)
    form = await request.form()
    try:
        serviceHear(request.app.state.application).hearInBackground(live, form.get("words", ""))
    except ValueError as error:
        raise HTTPException(400, str(error))
    return {"ok": True}


@router.post("/conversations/{conversationId}/think")
def conversationThink(request: Request, conversationId: str):
    _, live = owned(request, conversationId)
    return {"messages": serviceThink().think(live)}


@router.post("/conversations/{conversationId}/leave")
def conversationLeave(request: Request, conversationId: str):
    application = request.app.state.application
    live = application.conversations.get(conversationId)
    if live is not None:
        person = serviceWhoIsThis(application).person(request)
        if person is not None and (live.owner == person.email or person.isAdministrator()):
            serviceLeave(application).leave(live)
    return {"ok": True}


@router.get("/conversations/{conversationId}/stream")
def conversationStream(request: Request, conversationId: str):
    owned(request, conversationId)
    return StreamingResponse(request.app.state.application.streams.follow(f"conversation:{conversationId}"),
                             media_type="text/event-stream")


@router.get("/conversations/{conversationId}/state")
def conversationState(request: Request, conversationId: str):
    person, live = owned(request, conversationId)
    if person.level < 2:
        raise HTTPException(403, "the inner life is shown to friends and administrators")
    return JSONResponse(serviceConversationState().state(live))
