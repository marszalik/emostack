import json
import os


class promptTemplate:
    """A .prompt file: named blocks of text sent to the LLM model.

    A block starts with a line `@@ name` and runs to the next such line. The newline that
    precedes the next header is not part of the block, so a block keeps every other line and
    space exactly as written. Placeholders are «NAME» and are filled by `fill`."""

    _cache = {}

    def __init__(self, path):
        self.path = path
        self.blocks = self._load(path)

    @classmethod
    def beside(cls, moduleFile, fileName):
        """The template that sits in the same package as the module `moduleFile`."""
        path = os.path.join(os.path.dirname(os.path.abspath(moduleFile)), fileName)
        if path not in cls._cache:
            cls._cache[path] = cls(path)
        return cls._cache[path]

    def text(self, name):
        if name not in self.blocks:
            raise KeyError(f"no block '{name}' in {self.path}")
        return self.blocks[name]

    def fill(self, name, **values):
        text = self.text(name)
        for key, value in values.items():
            text = text.replace(f"«{key}»", str(value))
        return text

    def json(self, name):
        return json.loads(self.text(name))

    @staticmethod
    def _load(path):
        blocks = {}
        name = None
        lines = []
        with open(path, encoding="utf-8") as f:
            content = f.read()
        for line in content.split("\n"):
            if line.startswith("@@ "):
                if name is not None:
                    blocks[name] = "\n".join(lines)
                name = line[3:].strip()
                lines = []
            elif name is not None:
                lines.append(line)
        if name is not None:
            if lines and lines[-1] == "":
                lines = lines[:-1]
            blocks[name] = "\n".join(lines)
        return blocks
