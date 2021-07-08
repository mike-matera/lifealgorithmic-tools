"""
Helpers for files.
"""

import pathlib
import random 
import subprocess
import pwd
import os 

from lifealgorithmic.secrets import secret

class RandomPath:
    """
    Get random extant files or directories on the system.
    """

    DEFAULT_PATHS = [
        '/etc',
        '/bin',
        '/dev',
        '/usr/bin',
        '/usr/sbin',
        '/usr/share/doc',
    ]

    def __init__(self, search=DEFAULT_PATHS):
        self.docs = []
        for path in search:
            self.docs += list(pathlib.Path(path).glob('**/*'))

    def random_file(self):
        return self.find(lambda c: c.is_file() and not c.is_symlink())

    def random_dir(self):
        return self.find(lambda c: c.is_dir() and not c.is_symlink())

    def find(self, filt):
        """Search the candidate files until a condition matches."""
        return random.choice(list(filter(filt, self.docs)))

def setup_files(files, basedir=None, mode="overwrite"):
    """
    Setup a file structure. files is a sequence of three-tuples: 
        (path, mode, contents) 

    - If startdir is specified the path is deleted and re-created every time.
        this basically implies overwrite. 

    - mode is "overwrite" or "once"
        overwite: Overwrite the file if it exists. 
        once: Skip write and chmod if it exists. 
    """

    if basedir is not None:
        subprocess.run(f"rm -rf {basedir}", shell=True)
        subprocess.run(f"mkdir -p {basedir}", shell=True)
    else:
        basedir = pathlib.Path(".")

    for path, mode, contents in files:
        target = basedir / path
        if mode == 'overwrite' or not target.exists():
            subprocess.run(f'mkdir -p {target.parent}', shell=True)
            with open(target, 'w') as fh:
                fh.write(contents)
            subprocess.run(f"chmod {mode} {target}", shell=True)


def check_files(self, files, startdir=pathlib.Path(".")):
    """
    Check the contents of files. files is the three-tuple from setup_files.         
    """
    for path, mode, contents in files:
        with open(startdir / path) as fh:
            assert contents == fh.read(), f"The contents of {path} don't match."
        stat = os.stat(startdir / path)
        rmode = oct(stat.st_mode & 0b111111111)[2:]
        assert mode == rmode, f"The permissions on {path} don't match."


def make_flag():
    """
    Create the flag file if it doesn't exist. Set the pathname and the secret file into the 
    secrets store. 
    
        Secrets:
            flag.path: <pathname>
            flag.secret: <secret file pathname>
    """
    global randpath
    flag_file = pathlib.Path('flag').resolve()
    if not flag_file.exists():
        gecos = pwd.getpwuid(os.getuid())[4]
        secret_file = randpath.random_file()
        flag_text = f"""

    Welcome {gecos.split(',')[0]} to the SUN-HWA. 
    There's trouble on the island today!

    Your secret file is: {secret_file}

"""
        with open(flag_file, 'w') as fh:
            fh.write(flag_text)
        secret.put('flag.path', str(flag_file))
        secret.put('flag.secret', str(secret_file))
# 
# For convenience 
#
randpath = RandomPath()
