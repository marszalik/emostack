"""Lets time pass for every being on the server: reflection after silence, sleep after a long one,
folding and forgetting in sleep. Each store runs on its owner's model. Run it from cron:

    * * * * *  cd /path/to/emostack && EMOSTACK_WEB_CONFIG=... python3 apps/web-emostack/tick.py
"""
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))
sys.path.insert(0, root)
sys.path.insert(0, here)

from emostack.core.config import config
from emostack.runtime.engine import engine
from domains.auth.Person import Person
from domains.auth.serviceWhoIsThis import serviceWhoIsThis
from domains.beings.serviceStoreFor import serviceStoreFor
from domains.core.application import application
from domains.models.serviceConnect import serviceConnect


def main():
    web = application(root, os.environ.get("EMOSTACK_WEB_CONFIG", os.path.join(here, "config.json")))
    connect = serviceConnect(web)
    levels = serviceWhoIsThis(web)
    for email, store in serviceStoreFor(web).owners():
        person = Person(email or "", level=Person.ADMINISTRATOR if email is None else levels.levelOf(email))
        if email is None:
            person.email = (web.config.adminEmails or [""])[0]
        if not connect.hasModel(person):
            continue
        mind = engine(config({"databasePath": store}), processor=connect.processor(person),
                      embedder=connect.embedder(person))
        try:
            mind.tick()
        except Exception as error:
            print(f"{store}: {error}", file=sys.stderr)
        finally:
            mind.close()


if __name__ == "__main__":
    main()
