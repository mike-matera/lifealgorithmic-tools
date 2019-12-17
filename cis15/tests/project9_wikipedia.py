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

from . import Project

raise NotImplementedError('This test needs refactoring.')

@generate_exercises(38, 39)
class Project9(Project) :

    def test_2_check_docstring(self):
        '''Your project file doesn't have a docstring.'''
        self.banner('Checking docstring') 
        filename = self.find_file('project9.py')
        self.assertIsNotNone(filename, "I can't find your project file (project9.py)")
        self.check_docstring(filename)

    def test_3_not_exists(self) :
        '''Your program didn't do the right thing when with a bogus page.''' 
        self.banner(f"Looking up a bogus Wikipedia article.")
        filename = self.find_file('project9.py')
        self.assertIsNotNone(filename, "I can't find your project file (project9.py)")
        article = 'aabaeasdf'
        with open(f'test_3_check_bogus.out', 'w') as log :
            test = pexpect.spawnu('python "' + filename.as_posix() + f'" "{article}"', logfile=log, encoding='utf-8')
            got = test.expect([pexpect.EOF, "(?i)doesn't exist."])
            if got != 1 :
                self.fail("You didn't show me the required error.")
            
    def test_4_do_spell_obama(self) :
        '''Your program gave me different words than I was expecting.'''
        self.do_check('Barack Obama', ['ii', 'obamacare', 'dodd', 'reinvestment', 'reauthorization', 'muammar', 'gaddafi', 'gaddafi', 'nato', 'osama', 'qaeda', 'anwar', 'awlaki', 'inclusiveness', 'lgbt', 'obergefell', 'isil',])

    def test_5_do_spell_blues(self) :
        '''Your program gave me different words than I was expecting.'''
        self.do_check('Twelve-bar blues', ['iv'])

    def test_6_do_spell_snooker(self) :
        '''Your program gave me different words than I was expecting.'''
        self.do_check('2018 World Snooker Championship', ['betfred', 'bbc', 'eurosport', 'selby', 'junhui', 'selby', 'reardon', 'reardon',])

    def do_check(self, article, words) :
        self.banner(f"Looking up Wikipedia article {article}.")
        words = [ f'(?i){word}' for word in words ]
        filename = self.find_file('project9.py')
        self.assertIsNotNone(filename, "I can't find your project file (project9.py)")

        with open(f'test_check_{article}.out', 'w') as log :
            test = pexpect.spawnu('python "' + filename.as_posix() + f'" "{article}"', logfile=log, encoding='utf-8')
            for word in words : 
                got = test.expect([pexpect.EOF] + words, timeout=5)
                if got == 0 :
                    self.fail("I didn't expect to see a word you gave me")
                
            test.close()
        
if __name__ == '__main__' : 
    unittest.main(verbosity=0, exit=False)
