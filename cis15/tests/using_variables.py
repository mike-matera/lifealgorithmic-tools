import unittest
import pexpect
import re

from . import Project


class UsingVariables(Project):

    def __init__(self, *args):
        super().__init__('using_variables.py', *args, do_import=False)

    def test_01_check_docstring(self):
        """Your file doesn't seem to have the right docstring"""
        self.banner("Checking to see if your project has a docstring. ")
        self.check_docstring()

    def test_02_check_output(self):
        """Your program didn't produce the number that I expected."""
        self.banner('Checking to see if your program outpus the correct number.')
        test = pexpect.spawnu(f'python "{self.find_file()}"')
        self.assertNotEqual(0, test.expect([pexpect.EOF, "31556925"]))

    def test_03_check_hardcode(self):
        """Your program contains the number 31556925 in the code and it probably shouldn't"""
        self.banner("Checking to see if your number is hard-coded.")
        with open(self.find_file()) as py:
            for l in py.readlines():
                if re.search(r'31556925', l) is not None:
                    if not re.search(r'#.*31556925', l) is not None:
                        self.fail('I found the number 31556925 in your code and not in a comment!')


if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
