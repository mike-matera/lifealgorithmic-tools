import unittest
import logging 
import sys 
import pexpect
import random
import os
import time
import importlib
import importlib.util
import tempfile

from selenium import webdriver

from . import Project

raise NotImplementedError('This test needs refactoring.')

@generate_exercises(38, 39)
class SpellCheckWikipedia(Project) :

    def test_0_check_docstring(self):
        """Your program should have a docstring"""
        self.banner("Looking for your program's docstring.")
        filename = self.find_file('project10.py')
        self.assertIsNotNone(filename, "I can't find your project file (project10.py)")
        self.check_docstring(filename)

    def test_1_check_python(self) :
        """I didn't see the words I expected."""
        self.banner("Spell checking the 'Python' article.")
        filename = self.find_file('project10.py')
        self.assertIsNotNone(filename, "I can't find your project file (project10.py)")
        with open('test_1_check_python.out', 'w') as log:
            test = pexpect.spawnu('python "' + filename.as_posix() + '" "Python_(programming_language)"', logfile=log, encoding='utf-8')
            got = test.expect([pexpect.EOF, 'whitespace'])
            if got == 0:
                self.fail('I expected to see the word "whitespace" and I never saw it.')
            test.close()
            
            
if __name__ == '__main__' : 
    unittest.main(verbosity=0, exit=False)
