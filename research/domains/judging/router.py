from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from research.domains.judging.repositoryJudges import repositoryJudges
from research.domains.judging.serviceDeleteJudge import serviceDeleteJudge
from research.domains.judging.serviceSaveJudge import serviceSaveJudge
from research.domains.models.repositoryModels import repositoryModels

router = APIRouter()


@router.get("/judges", response_class=HTMLResponse)
def judgesPage(request: Request):
    application = request.app.state.application
    return application.page("judges.mako", title="Judges", section="judges",
                            judges=repositoryJudges(application.database).all(),
                            models=[m for m in repositoryModels(application.database).all() if m["kind"] == "chat"])


@router.post("/judges")
async def judgeCreate(request: Request):
    serviceSaveJudge(repositoryJudges(request.app.state.application.database)).save(dict(await request.form()))
    return RedirectResponse("/judges", status_code=303)


@router.post("/judges/{judgeId}")
async def judgeUpdate(request: Request, judgeId: int):
    serviceSaveJudge(repositoryJudges(request.app.state.application.database)).save(dict(await request.form()), judgeId)
    return RedirectResponse("/judges", status_code=303)


@router.post("/judges/{judgeId}/delete")
def judgeDelete(request: Request, judgeId: int):
    serviceDeleteJudge(repositoryJudges(request.app.state.application.database)).delete(judgeId)
    return RedirectResponse("/judges", status_code=303)
