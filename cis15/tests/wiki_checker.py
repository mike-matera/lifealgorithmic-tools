import unittest
import pexpect
import sys
import os
import random

from pathlib import Path
from . import Project


class WikiChecker(Project):
    """Check the Wikipedia fetch project with Spell Check."""

    def __init__(self, *args):
        super().__init__('wiki_checker.py', *args)

    def test_01_docstring(self):
        """Your file doesn't seem to have the right docstring"""
        self.banner("Checking to see if your project has a docstring. ")
        self.check_docstring()

    def test_02_check_bad(self):
        """You didn't print "ERROR" in response to a bad article."""
        self.banner("Testing what happens when I give your program a bad article.")
        with pexpect.spawnu('python3', [self.projfile], timeout=1, logfile=None) as test:
            test.sendline('blahblasdfa8ahblah')
            if test.expect([pexpect.TIMEOUT, pexpect.EOF, "(?i)error"]) < 2:
                self.fail("I didn't see the word ERROR from your program!")

    def test_03_check_good(self):
        """You didn't print the article summary for "Guy Fawkes"."""
        self.banner("Testing what happens when I give your program a good article.")
        with pexpect.spawnu('python3', [self.projfile], timeout=1, logfile=None) as test:
            test.sendline('Guy Fawkes')
            if test.expect([pexpect.TIMEOUT, pexpect.EOF, "Guido Fawkes"]) < 2:
                self.fail("I didn't see the extract from the article!")

    def test_04_quit(self):
        """Your program didn't quit when I entered quit"""
        self.banner("Testing what happens when I run the quit command.")
        with pexpect.spawnu('python3', [self.projfile], timeout=1, logfile=None) as test:
            test.sendline('quit')
            if test.expect([pexpect.TIMEOUT, pexpect.EOF]) < 1:
                self.fail("Your program didn't quit when I typed quit!")

    def test_05_multi(self):
        """I entered multiple articles and it seems that something went wrong."""
        with pexpect.spawnu('python3', [self.projfile], timeout=1, logfile=None) as test:
            self.banner("Testing multiple commands.")

            test.sendline('blahblasdfa8ahblah')
            if test.expect([pexpect.TIMEOUT, pexpect.EOF, "(?i)error"]) < 2:
                self.fail("I didn't see the word ERROR from your program!")

            test.sendline('Guy Fawkes')
            if test.expect([pexpect.TIMEOUT, pexpect.EOF, "Guido Fawkes"]) < 2:
                self.fail("I didn't see the extract from the article!")

            test.sendline('quit')
            if test.expect([pexpect.TIMEOUT, pexpect.EOF]) < 1:
                self.fail("Your program didn't quit when I typed quit!")

    def test_06_extra_credit(self):
        with pexpect.spawnu('python3', [self.projfile], timeout=1, logfile=None) as test:
            self.banner("Testing for extra credit: Looking up Guy Fawkes")

            test.sendline('Guy Fawkes')
            if test.expect([pexpect.TIMEOUT, pexpect.EOF, "(?i)extra credit"]) < 2:
                self.skipTest("Skipping test because I didn't see the words EXTRA CREDIT.")

            expected = "Wintour Wintour"
            if test.expect([pexpect.TIMEOUT, pexpect.EOF, f"(?i){expected}"]) < 2:
                self.fail("I didn't see the word list I expected: " + expected)

if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)