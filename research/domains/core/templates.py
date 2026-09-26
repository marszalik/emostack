import glob
import os

from mako.lookup import TemplateLookup


class templates:
    """Mako over the views of every domain. A view is found by its file name; names are unique
    across domains."""

    def __init__(self, domainsFolder):
        folders = sorted(glob.glob(os.path.join(domainsFolder, "*", "views")))
        self.lookup = TemplateLookup(directories=folders, input_encoding="utf-8", strict_undefined=False)

    def render(self, name, **values):
        return self.lookup.get_template(name).render(**values)
