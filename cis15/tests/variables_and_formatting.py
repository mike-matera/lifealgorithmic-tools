import sys
import unittest
import subprocess

from . import Project


class UsingVariables(Project):

    def __init__(self, *args):
        super().__init__('project_variables_and_formatting.ipynb', *args, do_import=False)

    def test_01_convert(self):
        """Failed to convert your Notebook to HTML!"""
        self.banner('Converting your notebook to HTML')
        got = subprocess.run(f"jupyter nbconvert {self.find_file(self.projfile)}", shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if got.returncode != 0:
            print('Failed to convert your notebook:')
            print(got.stderr.decode('utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
