import glob
import os

from mako.lookup import TemplateLookup


class templates:
    """Mako over the views of every domain; view names are unique across domains."""

    def __init__(self, domainsFolder):
        folders = sorted(glob.glob(os.path.join(domainsFolder, "*", "views")))
        self.lookup = TemplateLookup(directories=folders, input_encoding="utf-8")

    def render(self, name, **values):
        return self.lookup.get_template(name).render(**values)
