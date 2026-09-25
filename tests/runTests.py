"""Runs every test module under tests/: python3 tests/runTests.py"""
import os
import sys
import unittest

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

suite = unittest.TestSuite()
loader = unittest.TestLoader()
for folder, _, files in sorted(os.walk(os.path.join(root, "tests"))):
    for name in sorted(files):
        if name.startswith("test") and name.endswith(".py") and "support" not in folder:
            module = os.path.relpath(os.path.join(folder, name), root)[:-3].replace(os.sep, ".")
            suite.addTests(loader.loadTestsFromName(module))
result = unittest.TextTestRunner(verbosity=1).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
