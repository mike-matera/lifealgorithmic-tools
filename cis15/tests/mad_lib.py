import unittest
import logging 
import sys 
import pexpect
import random
import os
import time

from selenium import webdriver

from . import Project


class MadLib(Project):

    def __init__(self, *args):
        super().__init__('mad_lib.py', *args, do_import=False)

    def test_01_check_docstring(self):
        """Your file doesn't seem to have the right docstring"""
        self.banner("Checking to see if your project has a docstring.")
        self.check_docstring()

    def test_02_check_prompts(self):
        """You didn't ask me for a "noun", "verb" and "adjective" in the right order."""
        self.banner("Checking that you prompt me for the right words.")
        cmdline = f"""python3 "{self.projfile}" '{{noun}} {{adjective}} {{verb}}'"""
        with pexpect.spawnu(cmdline, timeout=1) as test:
            got = test.expect([pexpect.EOF, pexpect.TIMEOUT, '(?i)noun'])
            if got < 2:
                self.fail("""I expected to see the word "noun" """)
            test.sendline("x")
            got = test.expect([pexpect.EOF, pexpect.TIMEOUT, '(?i)verb'])
            if got < 2:
                self.fail("""I expected to see the word "verb" """)
            test.sendline("x")
            got = test.expect([pexpect.EOF, pexpect.TIMEOUT, '(?i)ajective'])
            if got == 2:
                self.fail("""I expected to see the word "adjective" """)

    def test_03_check_predictable(self):
        """You should have printed 'I ran into a blue Monday.'"""
        self.banner(f"Running python3 {self.projfile} 'I {{verb}} into a {{adjective}} {{noun}}'")
        if not self.generic_test('I {verb} into a {adjective} {noun}', "ran", "blue", "Monday"):
            self.fail("You didn't produce the correct output!")

    def test_04_check_predictable(self):
        """You should have printed 'The giant cat bounced freely!'"""
        self.banner(f"Running python3 {self.projfile} 'The {{adjective}} {{noun}} {{verb}} freely!'")
        if not self.generic_test('The {adjective} {noun} {verb} freely!', "cat", "giant", "bounced"):
            self.fail("You didn't produce the correct output!")

    def test_05_check_random(self):
        """I gave you a random Madlib and you didn't complete it correctly."""
        template = []
        for i in range(random.randint(5,10)):
            template.append(random.choice(self.words))
        template.insert(random.randint(0, len(template)-1), '{verb}')
        template.insert(random.randint(0, len(template)-1), '{adjective}')
        template.insert(random.randint(0, len(template)-1), '{noun}')
        template = ' '.join(template)
        verb = random.choice(self.words)
        noun = random.choice(self.words)
        adj = random.choice(self.words)
        self.banner(f"""Testing madlib "{template}" with noun={noun}, verb={verb}, adjective={adj}""")
        self.generic_test(template, noun, verb, adj)

    def generic_test(self, template, noun, verb, adj):
        cmdline = f"""python3 "{self.projfile}" '{template}'"""
        expect = template.format(noun=noun, verb=verb, adjective=adj)
        with pexpect.spawnu(cmdline) as test:
            test.sendline(noun)
            test.sendline(verb)
            test.sendline(adj)
            got = test.expect([pexpect.EOF, expect])
            if got == 0:
                return False
        return True


if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)

