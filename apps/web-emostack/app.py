"""The web application: people bring their own model and talk with their beings; friends and
administrators also see the being's inner life. Every folder in domains/ that has a router.py is
part of the application, so that a deployment can add a domain of its own, such as a sign-in.

    EMOSTACK_WEB_CONFIG=config.json uvicorn app:build --factory --app-dir apps/web-emostack --port 8093
    python3 apps/web-emostack/app.py --port 8093
"""
import argparse
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))
sys.path.insert(0, root)
sys.path.insert(0, here)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import importlib

from domains.auth.serviceWhoIsThis import serviceWhoIsThis
from domains.core.application import application

openPaths = ("/auth/", "/static/", "/healthz")


def build():
    app = FastAPI(title="EmoStack")
    app.state.application = application(root, os.environ.get("EMOSTACK_WEB_CONFIG", os.path.join(here, "config.json")))
    for name in sorted(os.listdir(os.path.join(here, "domains"))):
        static = os.path.join(here, "domains", name, "static")
        if os.path.isdir(static):
            app.mount(f"/static/{name}", StaticFiles(directory=static), name=f"static{name}")

    @app.middleware("http")
    async def gate(request: Request, callNext):
        """Nothing but signing in is open to someone without the level the settings require."""
        web = request.app.state.application
        needed = int(web.config.requireLoginLevel)
        if needed <= 0 or request.url.path.startswith(openPaths):
            return await callNext(request)
        who = serviceWhoIsThis(web)
        person = who.person(request)
        if person is not None and person.level >= needed:
            return await callNext(request)
        status = 401 if person is None else 403
        if request.method != "GET" or "text/html" not in request.headers.get("accept", "text/html"):
            return JSONResponse({"detail": "sign in first" if person is None else "no access"}, status_code=status)
        return HTMLResponse(web.page("gate.mako", user=person.toDict() if person else None), status_code=status)

    @app.get("/healthz")
    def health():
        return {"ok": True}

    for name in sorted(os.listdir(os.path.join(here, "domains"))):
        if os.path.exists(os.path.join(here, "domains", name, "router.py")):
            app.include_router(importlib.import_module(f"domains.{name}.router").router)
    return app


if __name__ == "__main__":
    import uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8093)
    options = parser.parse_args()
    uvicorn.run(build(), host=options.host, port=options.port)
