from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from domains.auth.repositoryPeople import repositoryPeople
from domains.auth.serviceDeletePerson import serviceDeletePerson
from domains.auth.serviceEveryone import serviceEveryone
from domains.auth.serviceSavePerson import serviceSavePerson
from domains.auth.serviceWhoIsThis import serviceWhoIsThis
from domains.auth.sessionCookie import sessionCookie

router = APIRouter()


def administrator(request):
    person = serviceWhoIsThis(request.app.state.application).person(request)
    if person is None or not person.isAdministrator():
        raise HTTPException(403, "administrators only")
    return person


@router.get("/auth/logout")
def signOut():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(sessionCookie.name)
    return response


@router.get("/people", response_class=HTMLResponse)
def peoplePage(request: Request):
    person = administrator(request)
    application = request.app.state.application
    return application.page("people.mako", section="people", user=person.toDict(), level=person.level,
                            people=repositoryPeople(application.database).all(),
                            everyone=serviceEveryone(application, serviceWhoIsThis(application)).list(),
                            administrators=application.config.adminEmails)


@router.post("/people")
async def personSave(request: Request):
    administrator(request)
    form = await request.form()
    serviceSavePerson(repositoryPeople(request.app.state.application.database)).save(form.get("email"), form.get("level"))
    return RedirectResponse("/people", status_code=303)


@router.post("/people/delete")
async def personDelete(request: Request):
    administrator(request)
    application = request.app.state.application
    form = await request.form()
    serviceDeletePerson(repositoryPeople(application.database), application.config).delete(form.get("email"))
    return RedirectResponse("/people", status_code=303)
