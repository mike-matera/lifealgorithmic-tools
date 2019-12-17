import unittest
import pexpect
import os
import random

from pathlib import Path
from . import Project


def do_setup(cls):
    template = []
    for i in range(random.randint(5, 10)):
        template.append(random.choice(cls.words))
    template.insert(random.randint(0, len(template) - 1), '{}')
    template.insert(random.randint(0, len(template) - 1), '{}')
    template.insert(random.randint(0, len(template) - 1), '{}')
    cls.template = ' '.join(template)

    cls.types = []
    cls.values = []
    for _ in range(3):
        cls.types.append(random.choice(cls.words))
        cls.values.append(random.choice(cls.words))

    cls.madfile = 'projtest_random_madlib.txt'
    cls.outfile = cls.madfile + '.complete'

    with open(cls.madfile, 'w') as f:
        f.write(cls.template + '\n')
        f.write('\n'.join(cls.types) + '\n')


class __MadLibsImproved:

    def test_01_check_docstring(self):
        """Your file doesn't seem to have the right docstring"""
        self.banner("Checking to see if your project has a docstring. ")
        self.check_docstring()

    def test_3_check_prompts(self):
        '''Your program should prompt for the word types that it reads in lines 2, 3 and 4 of the madlib input file.'''
        self.banner('Checking for the expected word prompts.')

        with open('projtest_check_prompts.log', 'w') as log:
            test = pexpect.spawnu(f'python3 "{self.projfile}" "{self.madfile}"', logfile=log, echo=False)
            for i in range(3):
                got = test.expect([pexpect.TIMEOUT, pexpect.EOF, self.types[i]], timeout=1)
                if got < 2:
                    self.fail('You never prompted me for a ' + self.types[i])
                test.sendline(self.values[i])
            test.close()

    def test_4_check_output(self):
        '''Your program did not produce the madlib that I expected. See the log files.''' 
        self.banner('Checking for the expected madlib.')

        test = pexpect.spawnu(f'python3 "{self.projfile}" "{self.madfile}"')
        for i in range(3):
            test.sendline(self.values[i])
        got = test.expect([pexpect.TIMEOUT, pexpect.EOF, self.template.format(*self.values)], timeout=1)
        if got < 2:
            self.fail("I didn't see the completed MadLib printed.")
        test.close()

    def test_5_check_file(self) :
        '''Your program didn't create and output file with the .complete suffix.'''
        self.banner('Checking the output file.')
        self.assertTrue(os.path.isfile(self.outfile), "I can't file the output file " + self.outfile)
        with open(self.outfile) as f:
            line = f.readline().strip()

        self.assertEqual(line, self.template.format(*self.values), "The madlib you saved doesn't match what I expected.")
        

class MadLibsImproved(Project, __MadLibsImproved):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        do_setup(cls)

    def __init__(self, *args):
        super().__init__('madlibs_improved.py', *args)

            
if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
