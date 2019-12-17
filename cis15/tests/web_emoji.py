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
import re

from selenium import webdriver

from . import Project

raise NotImplementedError('This test needs refactoring.')

@generate_exercises(23, 24, 25)
class WebEmojiEx(Project):
    pass

class WebEmoji(Project):

    def setUp(self) :
        filename = self.find_file('web_emoji.py')
        if filename is None :
            raise unittest.SkipTest('No web_emoji.py is present.')
        self.driver = webdriver.Firefox()

    def tearDown(self) :
        self.driver.close()

    def do_url(self, url, exp):
        filename = self.find_file('web_emoji.py')
        wd = os.path.dirname(filename)
        with open('flask.out', 'w') as log :
            test = pexpect.spawnu(f'''bash -c ". ~/PythonGrader/env/bin/activate && python '{filename}'"''', logfile=log, cwd=wd)
            result = test.expect([pexpect.EOF, '0.0.0.0'])
            self.driver.get(f'http://localhost:8080/{url}')
            time.sleep(1)
            self.driver.get_screenshot_as_file(f'{url}.png')
            self.assertIsNotNone(re.search(exp, self.driver.page_source), "I didn't see the emoji I expected.")
            test.close()
            test.wait()

    def test_smiling_cat_face(self):
        """Your page didn't show me a smiling cat face."""
        self.banner("Testing your /smilingcatface URL")
        self.do_url('smilingcatface', '(😸|😺|😻|😍|💔|💓|💗)')

    def test_heart(self):
        """Your page didn't show me a heart."""
        self.banner("Testing your /heart URL")
        self.do_url('heart', '(❤|♥||💚)')

    def test_sunglasses(self):
        """Your page didn't show me a sunglasses face."""
        self.banner("Testing your /sunglasses URL")
        self.do_url('sunglasses', '(😎|🕶|👓)')

if __name__ == '__main__' : 
    unittest.main(verbosity=0, exit=False)
