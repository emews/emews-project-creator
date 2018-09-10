import unittest

#from .context import epc
#import epc

#print(dir(epc))
from epc import core

class TestCore(unittest.TestCase):

    def test_ctx_load(self):
        template_path = "./tests/test_data"
        tf = "foo.json"
        try:
            core.load_context(template_path, tf)
        except FileNotFoundError:
            pass
        else:
            self.assertTrue(False)

        tf = "bad.json"
        try:
           core.load_context(template_path, tf)
        except ValueError:
            pass
        else:
            self.assertTrue(False)

        tf = "bad.json"
        try:
           core.load_context(template_path, tf)
        except ValueError:
            pass
        else:
            self.assertTrue(False)

        ctx = core.load_context(template_path)
        self.assertEquals(1, len(ctx))
        self.assertEquals('my_project', ctx['project']['name'])