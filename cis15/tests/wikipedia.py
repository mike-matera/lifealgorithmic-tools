import unittest
import pexpect
import logging
import sys

from . import Project

class WikiFetch(Project):

    def __init__(self, *args):
        super().__init__('wikipedia.py', *args)

    def test_10_working_article(self):
        """You didn't give me what I expected for a good article."""
        self.banner('Looking for "Chernobyl disaster".')
        proj = self.load_file_safe(self.projfile)
        inst = proj.Wikipedia('Chernobyl disaster')
        self.assertTrue(inst.exists(), """You told me that "Chernobyl disaster" doesn't exist, but it does!""")
        self.assertTrue("nuclear" in inst.extract(), """I didn't see the article extract that I expected.""")

    def test_11_bogus_article(self):
        """You didn't give me what I expected for a bogus article."""
        self.banner('Looking for "Blah xxxyyyzzz".')
        proj = self.load_file_safe(self.projfile)
        inst = proj.Wikipedia('Blah xxxyyyzzz')
        self.assertFalse(inst.exists(), """You told me that "Blah xxxyyyzzz" exists, but it doesn't!""")


if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
