"""
Helpers for files.
"""

import pathlib
import random 
import subprocess
import pwd
import os 

from lifealgorithmic.linux.words import randword
from lifealgorithmic.secrets import vault

class RandomPath:
    """
    Get random extant files or directories on the system.
    """

    DEFAULT_PATHS = [
        ('/etc', '**/*'),
        ('/bin', '**/*'),
        ('/dev', '**/*'),
        ('/usr/bin', '**/*'),
        ('/usr/sbin', '**/*'),
        ('/usr/share', '*/*'),
        ('/sys', '*/*/*'),
        ('/boot', '**/*'),
        ('/lib', '*/*'),
    ]

    def __init__(self, search=DEFAULT_PATHS, debug=False):
        self.docs = None
        self.search = search
        self.debug = debug
    
    def _build(self):
        self.docs = []

        def can_stat(f):
            try:
                f.stat()
                return True
            except:
                return False 

        for path in self.search:
            inpath = list(filter(can_stat, pathlib.Path(path[0]).glob(path[1])))
            if self.debug:
                print(f"DEBUG: {path} yields {len(inpath)} files.")    
            self.docs.append(inpath)

    def random_file(self):
        return self.find(lambda c: c.is_file() and not c.is_symlink()).resolve()

    def random_dir(self):
        return self.find(lambda c: c.is_dir() and not c.is_symlink()).resolve()

    def find(self, filt):
        """Search the candidate files until a condition matches."""
        if self.docs is None:
            self._build()
        random.shuffle(self.docs)
        for path in self.docs:
            choices = list(filter(filt, path))
            if len(choices) > 0:
                return random.choice(choices)


def setup_files(files, basedir=None, createmode="overwrite"):
    """
    Setup a file structure. files is a sequence of four-tuples: 
        (path, (user, group), mode, contents) 

        (user, group) can be None, individual user and group can also be None
        mode can be None 
        contents can be None 

    - If basedir is specified the path is deleted and re-created every time.
        this basically implies overwrite. 

    - createmode is "overwrite" or "once"
        overwite: Overwrite the file if it exists. 
        once: Skip write and chmod if it exists. 
    """

    if basedir is not None:
        basedir = pathlib.Path(basedir)
        subprocess.run(f"rm -rf {basedir}", shell=True)
        subprocess.run(f"mkdir -p {basedir}", shell=True)
    else:
        basedir = pathlib.Path(".")

    for path, ownership, mode, contents in files:
        target = basedir / path
        if createmode == 'overwrite' or not target.exists():
            subprocess.run(f'mkdir -p {target.parent}', shell=True)
            with open(target, 'w') as fh:
                fh.write(contents)
            if mode is not None:
                subprocess.run(f"chmod {mode} {target}", shell=True)
            if ownership is not None:
                if ownership[0] is not None:
                    subprocess.run(f"chown {ownership[0]} {target}", shell=True)
                if ownership[1] is not None:
                    subprocess.run(f"chgrp {ownership[1]} {target}", shell=True)

def check_files(files, basedir=pathlib.Path(".")):
    """
    Check the contents of files. files is the four-tuple from setup_files.         
    """
    basedir = pathlib.Path(basedir)
    for path, ownership, mode, contents in files:
        path = basedir / path
        assert path.exists(), f"""The file {path} does not exist."""
        stat = path.stat()
        if contents is not None:
            with open(path) as fh:
                assert contents == fh.read(), f"The contents of {path} don't match."
        if mode is not None:
            rmode = stat.st_mode & 0b111111111
            assert mode == rmode, f"The permissions on {path} don't match."
        if ownership is not None:
            if ownership[0] is not None:
                assert stat.st_uid == ownership[0], f"""The owner of {path} doesn't match."""
            if ownership[1] is not None:
                assert stat.st_gid == ownership[1], f"""The group of {path} doesn't match."""

def make_flag():
    """
    Create the flag in the user's home directory if it doesn't exist. Set the pathname 
    and the secret file into the secrets store. 
    
        Secrets:
            flag.path: <pathname>
            flag.secret: <secret file pathname>
    """
    global randpath
    flag_file = pathlib.Path(f'{os.environ["HOME"]}/flag').resolve()
    if vault.get('flag.path') is None or vault.get('flag.secret') is None:
        gecos = pwd.getpwuid(os.getuid())[4]
        secret_file = randpath.random_file()
        flag_text = f"""

    Welcome {gecos.split(',')[0]} to the SUN-HWA. 
    There's trouble on the island today!

    Your secret file is: {secret_file}

"""
        with open(flag_file, 'w') as fh:
            fh.write(flag_text)
        vault.put('flag.path', str(flag_file))
        vault.put('flag.secret', str(secret_file))


def random_big_file(name='bigfile', shape=(100000, 12), sep=' ', end='\n'):
    """
    Create a large text file with dictionary words in the current directory.

    Sets:
        - bigfile.path: The path of the file. 
    """    
    bigfile = pathlib.Path(name).resolve()
    vault.put('bigfile.path', str(bigfile))

    with open(bigfile, 'w') as fh:
        for _ in range(shape[0]):
            for _ in range(shape[1]):
                fh.write(randword.choice() + sep)
            fh.write(end)
    
    return bigfile

def random_big_dir(count=1000):
    """
    Create a directory with a large number of randomly named files. 

    This function does not act on the filesystem. It only generates a 
    structure suitable for passing to `setup_files`. 
    """

    return list(map(lambda x: [x, None, None, x], random.sample(randword.choice(), count)))

# 
# For convenience 
#
randpath = RandomPath()
