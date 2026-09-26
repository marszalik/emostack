import os
import tempfile
import unittest

from emostack.core.promptTemplate import promptTemplate


class testPromptTemplate(unittest.TestCase):

    def testBlocksKeepSpacesAndBlankLines(self):
        path = os.path.join(tempfile.mkdtemp(), "sample.prompt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("@@ one\n  indented «NAME»\n\n@@ two\n\nstarts blank\n")
        template = promptTemplate(path)
        self.assertEqual(template.text("one"), "  indented «NAME»\n")
        self.assertEqual(template.text("two"), "\nstarts blank")
        self.assertEqual(template.fill("one", NAME="Maya"), "  indented Maya\n")
