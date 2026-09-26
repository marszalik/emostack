import re

from emostack.being.Temperament import Temperament


class serviceCreateBeing:
    """A new being with an empty memory. Only an administrator sets a temperament; everyone else's
    beings are neutral, as every being measured in the paper was."""

    namePattern = re.compile(r"^[A-Za-zŁÓŚĄĘĆŻŹŃłóśąęćżźń0-9 _-]{1,24}$")

    def __init__(self, engine, most):
        self.engine = engine
        self.most = most

    def create(self, person, form):
        name = (form.get("name") or "").strip()
        if not self.namePattern.match(name):
            raise ValueError("a name: letters, digits, spaces, up to 24 characters")
        if self.engine.beings.named(name) is not None:
            raise ValueError("there is already a being of that name")
        if not person.isAdministrator() and len(self.engine.beings.all()) >= self.most:
            raise ValueError(f"at most {self.most} beings per person — delete one first")
        temperament = Temperament()
        if person.isAdministrator():
            temperament = Temperament(max(-1.0, min(1.0, float(form.get("valenceBias") or 0))),
                                      max(0.1, min(3.0, float(form.get("intensityAmplification") or 1))),
                                      max(1.0, min(5.0, float(form.get("avoidanceWeight") or 2))))
        return self.engine.being(name, temperament)
