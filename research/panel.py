"""The research panel: scenarios, runs, experiments, judges.

    .venv/bin/python research/panel.py            # http://127.0.0.1:8090
    .venv/bin/python research/panel.py --port 8091
"""
import argparse
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from research.domains.core.application import application
from research.domains.experiments.router import router as experimentsRouter
from research.domains.judging.router import router as judgingRouter
from research.domains.lives.router import router as livesRouter
from research.domains.models.router import router as modelsRouter
from research.domains.scenarios.router import router as scenariosRouter


def build():
    app = FastAPI(title="EmoStack research panel")
    app.state.application = application(root)
    domains = os.path.join(root, "research", "domains")
    for name in sorted(os.listdir(domains)):
        static = os.path.join(domains, name, "static")
        if os.path.isdir(static):
            app.mount(f"/static/{name}", StaticFiles(directory=static), name=f"static{name}")
    for router in (scenariosRouter, livesRouter, experimentsRouter, judgingRouter, modelsRouter):
        app.include_router(router)
    return app


if __name__ == "__main__":
    import uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    options = parser.parse_args()
    uvicorn.run(build(), host=options.host, port=options.port)
