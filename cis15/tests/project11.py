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

class Project11(Project) :
    def setUp(self) :
        filename = self.find_file('project11.py')
        if filename is None :
            raise unittest.SkipTest('No project11.py is present.')
        self.driver = webdriver.Firefox()

    def tearDown(self) :
        self.driver.close()

    def test_web(self):
        '''Something went wrong with your flask app.''' 
        self.banner('Testing that your program produces the correct table.') 
        filename = self.find_file('project11.py')
        wd = os.path.dirname(filename)
        with open('flask.out', 'w') as log :


            env = os.environ 
            a = random.uniform(-10000, 10000)
            b = random.uniform(-10000, 10000)
            env['VALUE_A'] = str(a)
            env['VALUE_B'] = str(b)
            test = pexpect.spawnu('python "' + filename.as_posix() + '"', 
                                  logfile=log, 
                                  cwd=wd, 
                                  env=env)

            result = test.expect([pexpect.EOF, '0.0.0.0'])
            self.driver.get('http://localhost:8080/')
            time.sleep(1)
            
            values = [
                a+b, a-b, a*b, a/b, a%b, a<b, a>b, a==b
            ]
            cells = self.driver.find_elements_by_tag_name('td')[1::2]
            for i, value in enumerate(values) : 
                self.assertEqual(str(value), cells[i].text)

            self.driver.get_screenshot_as_file('project11.png')

if __name__ == '__main__' : 
    unittest.main(verbosity=0, exit=False)
