import unittest
import random
import os

from . import Project, io_control
from .madlibs_improved import __MadLibsImproved, do_setup


class MadLibs00Regrade(Project, __MadLibsImproved):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        do_setup(cls)

    def __init__(self, *args):
        super().__init__('madlibs_functions.py', *args)


class MadLibs01Functions(Project):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        do_setup(cls)

    def __init__(self, *args):
        super().__init__('madlibs_functions.py', *args)

    def test_2_docstrings(self):
        '''Your functions should each have docstrings.'''
        self.banner("Checking your functions for docstrings.")
        proj = self.load_file_safe(self.projfile)
        self.assertIsNotNone(proj.read_madlib_file.__doc__,
                           "Your read_madlib_file() function doesn't have a docstring.")
        
        self.assertIsNotNone(proj.do_ask_word.__doc__,
                           "Your do_madlib_input() function doesn't have a docstring.")

        self.assertIsNotNone(proj.display_madlib.__doc__,
                            "Your display_madlib() function doesn't have a docstring.")

    def test_3_read_madlib_file(self):
        '''The read_madlib_file() function did not return what I expexed. See the log files.'''
        self.banner("Testing your read_madlib_file() function.")
        proj = self.load_file_safe(self.projfile)

        m, t1, t2, t3 = proj.read_madlib_file(self.madfile)
        self.assertEqual(self.template, m.strip(), "read_madlib_file() didn't return the right template (line 1) from the madlib file")
        self.assertEqual(self.types[0], t1.strip(), "read_madlib_file() didn't return the right word type (line 2) from the madlib file")
        self.assertEqual(self.types[1], t2.strip(), "read_madlib_file() didn't return the right word type (line 3) from the madlib file")
        self.assertEqual(self.types[2], t3.strip(), "read_madlib_file() didn't return the right word type (line 4) from the madlib file")

    def test_4_do_madlib_input(self):
        '''The do_madlib_input() function did not return the words I entered.'''
        self.banner("Testing your do_madlib_input() function.")
        proj = self.load_file_safe(self.projfile)
        words = []
        with io_control('\n'.join(self.words)) as stdout:
            for type in self.types:
                words.append(proj.do_ask_word(type))

        for i, word in enumerate(words):
            self.assertEqual(word.strip(), self.words[i].strip(), "You didn't ask for a word type that I expected.")

    def test_5_display_madlib(self):
        '''The display_madlib() function didn't work as expected.''' 
        self.banner("Testing your display_madlib() function.")
        proj = self.load_file_safe(self.projfile)
        complete = self.template.format(*self.values)
        with io_control('') as stdout:
            proj.display_madlib(complete, self.outfile)
            got = stdout.getvalue().strip()

        self.assertEqual(complete, got, "You didn't print the MadLib that I expected.")
        self.assertTrue(os.path.exists(self.outfile),
                        "I asked you to create {} and I don't see it.".format(self.outfile))

            
if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)

