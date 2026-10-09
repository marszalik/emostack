import threading
import uuid

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from domains.auth.serviceWhoIsThis import serviceWhoIsThis
from domains.public.serviceRoom import serviceRoom

router = APIRouter()
starting = threading.Lock()


def roomOf(request):
    application = request.app.state.application
    if not application.config.publicSheep or not application.config.publicSheep.get("processor"):
        raise HTTPException(404, "there is no public sheep here")
    with starting:
        room = getattr(application, "publicRoom", None)
        if room is None:
            room = application.publicRoom = serviceRoom(application)
    return room


def visitorOf(request):
    """A visitor is known by a cookie that says nothing about them, and by their address. Returns the
    visitor, the address, and whether the cookie is new and must be set on the response."""
    visitor = request.cookies.get("visitor", "")
    fresh = len(visitor) != 32 or not all(c in "0123456789abcdef" for c in visitor)
    if fresh:
        visitor = uuid.uuid4().hex
    address = request.headers.get("x-real-ip") or (request.client.host if request.client else "")
    return visitor, address, fresh


def withCookie(response, request, visitor, fresh):
    if fresh:
        response.set_cookie("visitor", visitor, max_age=365 * 86400, httponly=True, samesite="lax",
                            secure=request.headers.get("x-forwarded-proto", request.url.scheme) == "https")
    return response


def failing(action):
    try:
        return action()
    except PermissionError as error:
        raise HTTPException(409, str(error))
    except ValueError as error:
        raise HTTPException(400, str(error))


def roomPage(request):
    application = request.app.state.application
    room = roomOf(request)
    visitor, _, fresh = visitorOf(request)
    person = serviceWhoIsThis(application).person(request)
    html = application.page("room.mako", section="room", user=person.toDict() if person else None,
                            level=person.level if person else 0, being=room.name)
    return withCookie(HTMLResponse(html), request, visitor, fresh)


@router.get("/public", response_class=HTMLResponse)
def publicPage(request: Request):
    return roomPage(request)


@router.get("/public/room")
def publicRoom(request: Request):
    room = roomOf(request)
    visitor, address, fresh = visitorOf(request)
    room.seen(visitor)
    data = {"status": room.status(visitor, address), "about": room.about(), "log": room.log(), "inner": room.inner()}
    return withCookie(JSONResponse(data), request, visitor, fresh)


@router.post("/public/queue")
async def publicQueue(request: Request):
    room = roomOf(request)
    visitor, address, fresh = visitorOf(request)
    form = await request.form()
    placed = failing(lambda: room.join(visitor, address, form.get("name")))
    return withCookie(JSONResponse(placed), request, visitor, fresh)


@router.post("/public/say")
async def publicSay(request: Request):
    room = roomOf(request)
    visitor, _, _ = visitorOf(request)
    form = await request.form()
    failing(lambda: room.say(visitor, form.get("words")))
    return {"ok": True}


@router.post("/public/leave")
async def publicLeave(request: Request):
    room = roomOf(request)
    visitor, _, _ = visitorOf(request)
    room.leave(visitor)
    return {"ok": True}


@router.post("/public/mail")
async def publicMail(request: Request):
    room = roomOf(request)
    visitor, address, fresh = visitorOf(request)
    form = await request.form()
    failing(lambda: room.mail(visitor, address, form.get("name"), form.get("words")))
    return withCookie(JSONResponse({"ok": True}), request, visitor, fresh)


@router.post("/public/report")
async def publicReport(request: Request):
    room = roomOf(request)
    visitor, address, _ = visitorOf(request)
    form = await request.form()
    room.report(visitor, address, form.get("about", ""), form.get("note", ""))
    return {"ok": True}


@router.get("/public/stream")
def publicStream(request: Request):
    room = roomOf(request)
    return StreamingResponse(request.app.state.application.streams.follow(room.KEY), media_type="text/event-stream")


def administrator(request):
    person = serviceWhoIsThis(request.app.state.application).person(request)
    if person is None or not person.isAdministrator():
        raise HTTPException(403, "administrators only")
    return person


@router.post("/public/admin/{action}")
def publicAdmin(request: Request, action: str):
    administrator(request)
    room = roomOf(request)
    if action == "sleep":
        room.rest(True)
    elif action == "wake":
        room.rest(False)
    elif action == "clear":
        room.leave(None, force=True)
    else:
        raise HTTPException(404, "sleep, wake or clear")
    return {"ok": True}


@router.get("/public/admin/reports")
def publicReports(request: Request):
    administrator(request)
    return JSONResponse(roomOf(request).visitors.reports())
