import io
import os 
import re
import sys
import uuid
import unittest
import importlib.util

from contextlib import contextmanager

from pathlib import Path


@contextmanager
def io_control(input_text=''):
    stdin_buf = io.StringIO(input_text)
    stdout_buf = io.StringIO()

    stdin = sys.stdin
    stdout = sys.stdout
    
    sys.stdin = stdin_buf
    sys.stdout = stdout_buf
    
    yield stdout_buf

    sys.stdin = stdin
    sys.stdout = stdout


class Project(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.words = []
        with open('/usr/share/dict/words') as d :
            for w in d.readlines():
                cls.words.append(w.strip())

    def __init__(self, filename, *args, **kwargs):
        self.projfile = filename
        super().__init__(*args)

    def setUp(self):
        self.filename = self.find_file(self.projfile)
        os.chdir(self.filename.parent)

    def find_file(self, name=None):
        if name is None:
            name = self.projfile
        files = list(Path(os.getcwd()).glob(f'**/{name}'))
        if len(files) == 0:
            raise unittest.SkipTest(f"Skipping tests because there's no file named {name}")
        return files[0]

    def load_file_safe(self, filename):
        stdin = sys.stdin
        stdout = sys.stdout
        sys.stdin = None
        sys.stdout = io.StringIO()
        try:
            mod = self.load_file(filename)
        except:
            raise self.fail("Test failed because there's code outside of a function.")
        finally:
            sys.stdin = stdin
            sys.stdout = stdout
        return mod

    def load_file(self, filename):
        mod_spec = importlib.util.spec_from_file_location(str(uuid.uuid4()), filename)
        mod = importlib.util.module_from_spec(mod_spec)
        mod_spec.loader.exec_module(mod)
        return mod

    def check_docstring(self):
        stdin = sys.stdin
        stdout = sys.stdout
        sys.stdin = None
        sys.stdout = io.StringIO()
        try:
            mod = self.load_file(self.projfile)
            self.assertIsNotNone(re.search(r'cis(\s*|-)15', mod.__doc__, re.I),
                                 "Your source file doesn't seem to have the right docstring")
        except Exception as e:
            # Fallback on pattern matching the file.
            with open(self.projfile) as f:
                contents = f.read()
            self.assertIsNotNone(re.search(r'cis(\s*|-)15', contents, re.I),
                                 "Your source file doesn't seem to have the right docstring")
        finally:
            sys.stdin = stdin
            sys.stdout = stdout

    def banner(self, banner):
        print('TEST : {}'.format(banner))
        sys.stdout.flush()

    @contextmanager
    def fail_on_input(self):
        stdin = sys.stdin
        stdout = sys.stdout

        sys.stdin = None
        sys.stdout = io.StringIO()

        try:
            yield

        except RuntimeError as e:
            self.fail("You used the input() function in a place you are not supposed to.")

        finally:
            sys.stdin = stdin
            sys.stdout = stdout 