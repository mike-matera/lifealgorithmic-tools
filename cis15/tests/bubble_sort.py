"""
Tests for the Bubble Sort project.
"""

import unittest
import random

from cis15.tests import Project, io_control


class TestBubbleSort(Project):

    def __init__(self, *args):
        super().__init__('bubble_sort.py', *args)

    def test_2_docstrings(self):
        '''Your functions should each have docstrings.'''
        proj = self.load_file_safe(self.projfile)
        self.banner("Checking your functions for docstrings.")
        self.assertIsNotNone(proj.bubble_swap.__doc__,
                             "Your bubble_swap() function doesn't have a docstring.")
        self.assertIsNotNone(proj.bubble_sort.__doc__,
                             "Your bubble_sort() function doesn't have a docstring.")

    @staticmethod
    def ref_swap(l, p):
        t = l[p]
        l[p] = l[p+1]
        l[p+1] = t
        return l

    @staticmethod
    def list_equal(k, l):
        if len(k) != len(l):
            return False
        for i in range(len(k)):
            if l[i] != k[i]:
                return False
        return True

    def test_3_swap_return_value(self):
        """The bubble_swap() function should return a list."""
        self.banner('Testing the return value of your bubble_swap() function.')
        proj = self.load_file_safe(self.projfile)
        l = proj.bubble_swap([0,1], 0)
        if not isinstance(l, list):
            self.fail("Your swap function doesn't return a list.")

    def test_4_swap(self):
        """There seems to be a problem with your bubble_swap() function."""
        self.banner('Testing your bubble_swap() function.')

        proj = self.load_file_safe(self.projfile)

        l = []
        for _ in range(10):
            l.append(random.randint(0, 100))

        for place in range(9):
            exp = TestBubbleSort.ref_swap(list(l), place)
            got = proj.bubble_swap(list(l), place)
            if not TestBubbleSort.list_equal(exp,got):
                self.fail(f"After calling bubble_swap({l}, {place}) you returned {got}")

    def test_5_sort_return_value(self):
        """The bubble_sort() function should return a list."""
        self.banner('Testing the return value of your bubble_sort() function.')
        proj = self.load_file_safe(self.projfile)
        l = proj.bubble_sort([0,1,2])
        if not isinstance(l, list):
            self.fail("Your swap function doesn't return a list.")

    def test_6_sort(self):
        """The bubble_sort() function should return a sorted list."""
        self.banner("Testing that your bubble_sort() function sorts.")
        proj = self.load_file_safe(self.projfile)
        for _ in range(10):
            l = []
            for _ in range(10):
                l.append(random.randint(-100, 100))

            got = proj.bubble_sort(list(l))
            if not TestBubbleSort.list_equal(sorted(l), got):
                self.fail(f'I asked you to sort {l} and you returned {got}.')


if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
