import unittest
import logging 
import sys 
import pexpect
import random
import os
import time

from selenium import webdriver

from . import Project

raise NotImplementedError('This test needs refactoring.')

@generate_exercises(6, 7, 8, 9)
class Project3(Project) : 

    def test_2_project3_docstring(self) :
        """Your project file doesn't seem to have the right docsctring."""
        self.banner("Checking the docstring in your program.")
        filename = self.find_file('project3.py')
        self.assertIsNotNone(filename, "I can't find your project file (project3.py)")
        self.check_docstring(filename)

    def test_3_run_project3(self) :
        """Your program didn't seem to output a table"""
        self.banner("Running your program and looking for a table.")
        filename = self.find_file('project3.py')
        self.assertIsNotNone(filename, "I can't find your project file (project3.py)")

        a = random.uniform(-10000, 10000)
        b = random.uniform(-10000, 10000)

        with open('run_project_3.txt', 'w') as log :
            test = pexpect.spawnu('python "' + filename.as_posix() + '"', logfile=log)

            test.sendline(f"{a}")
            test.sendline(f"{b}")

            #self.assertNotEqual(0, test.expect([pexpect.EOF, "(?i)<\s*table"]))
            self.assertNotEqual(0, test.expect([pexpect.EOF, f"{a}\+{b}"]))
                            


#class Project3Table(Project) :
class Project3Table() :
    def setUp(self) :
        filename = self.find_file('run_project_3.html')
        if filename is None :
            raise unittest.SkipTest('No HTML is present.')
        self.driver = webdriver.Firefox()

    def tearDown(self) :
        self.driver.close()

    def test_show_table(self) :
        '''Loading your table into a Chrome to see how it looks.'''
        self.banner("Checking the look of your HTML table.")
        filename = self.find_file('run_project_3.html')
        self.driver.get('file:///' + filename.as_posix() )
        self.driver.get_screenshot_as_file('table.png')

class Project3Advanced(Project) :
    def setUp(self) :
        filename = self.find_file('project3_adv.py')
        if filename is None :
            raise unittest.SkipTest('No project3_adv.py is present.')
        self.driver = webdriver.Firefox()

    def tearDown(self) :
        self.driver.close()

    def test_web(self):
        filename = self.find_file('project3_adv.py')
        wd = os.path.dirname(filename)
        with open('flask.out', 'w') as log :


            a = random.uniform(-10000, 10000)
            b = random.uniform(-10000, 10000)

            test = pexpect.spawnu('python "' + filename.as_posix() + '"', logfile=log, cwd=wd)

            test.sendline(f"{a}")
            test.sendline(f"{b}")
            test.sendline(f"{a}")
            test.sendline(f"{b}")

            result = test.expect([pexpect.EOF, '0.0.0.0'])
            self.driver.get('http://localhost:8080/')
            time.sleep(1)
            self.driver.get_screenshot_as_file('project3_adv.png')

if __name__ == '__main__' : 
    unittest.main(verbosity=0, exit=False)
