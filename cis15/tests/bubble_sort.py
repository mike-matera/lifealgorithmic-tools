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
        o = (p + 1) % len(l)
        l[o], l[p] = l[p], l[o]

    @staticmethod
    def list_equal(k, l):
        if len(k) != len(l):
            return False
        for i in range(len(k)):
            if l[i] != k[i]:
                return False
        return True

    def x_test_3_swap_return_value(self):
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

        exp = list(l)
        got = list(l)
        for place in range(10):
            TestBubbleSort.ref_swap(exp, place)
            with self.fail_on_input():
                proj.bubble_swap(got, place)
            if not TestBubbleSort.list_equal(exp, got):
                self.fail(f"After calling bubble_swap({l}, {place}) you returned {got}")

    def test_5_sort_return_value(self):
        """The bubble_sort() function should return a list."""
        self.banner('Testing the return value of your bubble_sort() function.')
        proj = self.load_file_safe(self.projfile)
        with self.fail_on_input():
            l = proj.bubble_sort([0,1,2])
        if not isinstance(l, list):
            self.fail("Your swap function doesn't return a list.")

    def test_6_sort_copy(self):
        """The bubble_sort() function should not modify the original list."""
        self.banner("Testing that your bubble_sort() function makes a copy.")
        proj = self.load_file_safe(self.projfile)
        for _ in range(10):
            l = []
            for _ in range(10):
                l.append(random.randint(-100, 100))

            copy = list(l)
            with self.fail_on_input():
                got = proj.bubble_sort(copy)

            if got == copy:
                self.fail(f'Your bubble sort function returned the list it was given, not a copy.')

            if not TestBubbleSort.list_equal(copy, l):
                self.fail(f"""You changed the list I passed to bubble_sort()""")

    def test_7_sort(self):
        """The bubble_sort() function should return a sorted list."""
        self.banner("Testing that your bubble_sort() function sorts.")
        proj = self.load_file_safe(self.projfile)
        for _ in range(10):
            l = []
            for _ in range(10):
                l.append(random.randint(-100, 100))

            with self.fail_on_input():
                got = proj.bubble_sort(list(l))

            if not TestBubbleSort.list_equal(sorted(l), got):
                self.fail(f'I asked you to sort {l} and you returned {got}.')


if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
