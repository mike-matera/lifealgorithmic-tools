"""
Module with helpers for Linux tests.
"""

import re
import os
import hashlib
import subprocess
import tempfile
import pathlib
import traceback

import lifealgorithmic.secrets

class Formatting:
    Bold = "\x1b[1m"
    Dim = "\x1b[2m"
    Italic = "\x1b[3m"
    Underlined = "\x1b[4m"
    Blink = "\x1b[5m"
    Reverse = "\x1b[7m"
    Hidden = "\x1b[8m"
    # Reset part
    Reset = "\x1b[0m"
    Reset_Bold = "\x1b[21m"
    Reset_Dim = "\x1b[22m"
    Reset_Italic = "\x1b[23m"
    Reset_Underlined = "\x1b[24"
    Reset_Blink = "\x1b[25m"
    Reset_Reverse = "\x1b[27m"
    Reset_Hidden = "\x1b[28m"


class Color:
    # Foreground
    F_Default = "\x1b[39m"
    F_Black = "\x1b[30m"
    F_Red = "\x1b[31m"
    F_Green = "\x1b[32m"
    F_Yellow = "\x1b[33m"
    F_Blue = "\x1b[34m"
    F_Magenta = "\x1b[35m"
    F_Cyan = "\x1b[36m"
    F_LightGray = "\x1b[37m"
    F_DarkGray = "\x1b[90m"
    F_LightRed = "\x1b[91m"
    F_LightGreen = "\x1b[92m"
    F_LightYellow = "\x1b[93m"
    F_LightBlue = "\x1b[94m"
    F_LightMagenta = "\x1b[95m"
    F_LightCyan = "\x1b[96m"
    F_White = "\x1b[97m"
    # Background
    B_Default = "\x1b[49m"
    B_Black = "\x1b[40m"
    B_Red = "\x1b[41m"
    B_Green = "\x1b[42m"
    B_Yellow = "\x1b[43m"
    B_Blue = "\x1b[44m"
    B_Magenta = "\x1b[45m"
    B_Cyan = "\x1b[46m"
    B_LightGray = "\x1b[47m"
    B_DarkGray = "\x1b[100m"
    B_LightRed = "\x1b[101m"
    B_LightGreen = "\x1b[102m"
    B_LightYellow = "\x1b[103m"
    B_LightBlue = "\x1b[104m"
    B_LightMagenta = "\x1b[105m"
    B_LightCyan = "\x1b[106m"
    B_White = "\x1b[107m"


class LinuxTest:

    def __init__(self, secret, testconfig=pathlib.Path('.tconfig')):
        self.score = 0
        self.total = 0
        self.secret = secret
        self.debug = False
        self.questions = []
        self.configfile = testconfig
        self.config = {}
        self.loadconfig()

    def __del__(self):
        self.print_cfm()

    def storeconfig(self):
        if self.debug:
            print("DEBUG: store: config:", self.config)
        lifealgorithmic.secrets.store_file(self.configfile, self.secret, self.config)

    def loadconfig(self):
        if not self.configfile.exists():
            self.storeconfig()
        self.config = lifealgorithmic.secrets.load_file(self.configfile, self.secret)
        if self.debug:
            print("DEBUG: load: config:", self.config)

    def print_cfm(self):
        print (Formatting.Bold, end='')
        print('Your final score is', self.score, 'out of', self.total)
        print('Your confirmation number is:', lifealgorithmic.secrets.generate_code({'score': self.score}, self.secret))
        print('''Please enter your confirmation number into Canvas.\nYou can restart the test any time.\n\n''')
        print (Formatting.Reset, end='')

    def get_nodehash(self):
        ipaddr = subprocess.check_output('ip addr', shell=True).decode('UTF-8')
        m = re.search('link/ether\s+(\S+)', ipaddr)
        mac = m.group(1)
        h = hashlib.md5()
        h.update(self.secret.encode())
        h.update(mac.encode())
        return int.from_bytes(h.digest(), byteorder='big')

    def tar_easteregg(self, tarfile):
        egg = self.get_nodehash()
        url = 'https://github.com/python/cpython/archive/v2.7.16.tar.gz'
        hidepath = 'cpython-2.7.16/RISCOS/Modules'
        if not os.path.isfile(str(tarfile)):
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.check_call('wget -O - {} | tar -xzf -'.format(url), cwd=tmp, shell=True,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                with open(str(pathlib.Path(tmp) / hidepath / 'egg.txt'), 'w') as f:
                    f.write(repr(egg))
                    f.write("\n")
                subprocess.check_call('tar -czf {} .'.format(str(tarfile)), cwd=tmp, shell=True, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)

    def loopback_easteregg(self, fsfile):
        egg = self.get_nodehash()
        if not os.path.isfile(str(fsfile)):
            try:
                subprocess.check_call("dd if=/dev/zero of='" + str(fsfile) + "' bs=1M count=100", shell=True,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                loopdev = subprocess.check_output("losetup -f", shell=True).decode('UTF-8').strip()
                subprocess.check_call('losetup ' + loopdev + " '" + str(fsfile) + "'", shell=True)
                subprocess.check_call('mkfs.ext4 ' + loopdev, shell=True, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
                subprocess.check_call('mount ' + loopdev + ' /mnt', shell=True)
                with open('/mnt/egg.txt', 'w') as f:
                    f.write(repr(egg))
                    f.write('\n')
                subprocess.check_call('umount ' + loopdev, shell=True)
                subprocess.check_call('losetup -d ' + loopdev, shell=True)
            except Exception as e:
                print("INTERNAL ERROR: Fs/File creation failed. Attempting to clean up.")
                subprocess.call('umount ' + loopdev, shell=True)
                subprocess.call('losetup -d ' + loopdev, shell=True)
                os.remove(str(fsfile))
                raise e

    def input(self, prompt=None):
        if prompt is None:
            prompt = "answer: "
        return input(Color.F_LightYellow + prompt + Color.F_Default)

    def print_error(self, *stuff):
        print(Color.F_LightRed, end='')
        print(*stuff)
        print(Color.F_Default, end='')

    def print_success(self, *stuff):
        print(Color.F_LightGreen, end='')
        print(*stuff)
        print(Color.F_Default, end='')

    def question(self, points, setup=None, interactive=False):
        def _decorator(func):
            def _wrapper(*args, **kwargs):

                if interactive and self.config.get(func.__name__) is not None:
                    self.score += points
                    return

                if setup is not None:
                    setup()

                print(Formatting.Bold, end='')
                print('-' * 80)
                print(func.__name__, " (", points, " points)", sep='')
                print('-' * 80)
                print(Formatting.Reset, end='')
                if (func.__doc__ is not None):
                    print(func.__doc__.format(*args, **kwargs))

                try:
                    while True:
                        try:
                            rval = func(*args, **kwargs)
                            self.score += points
                            self.config[func.__name__] = 1 
                            self.storeconfig()
                            self.print_success('** Correct **')
                            return rval
                        except Exception as e:
                            self.print_error('Error:', e)
                            if self.debug:
                                traceback.print_exc()
                            got = self.input('Try again? (Y/n)? ').strip().lower()
                            if got.startswith('n'):
                                return None
                except (KeyboardInterrupt, EOFError) as e:
                    exit(-1)

            if self.total > -1:
                self.total += points

            return _wrapper

        return _decorator

    def setup_files(self, files, startdir=None, writemode="overwrite"):
        """
        Setup a file structure. files is a list of three-tuples: 
            (path, mode, contents) 

        - If startdir is specified the path is deleted and re-created every time. 
        - mode is "replace" or "once"
            replace: Overwrite the file if it exists. 
            once: Skip write/chmod if it exists. 
        """

        if startdir is not None:
            subprocess.run(f"rm -rf {startdir}", shell=True)
            subprocess.run(f"mkdir {startdir}", shell=True)
        else:
            startdir = pathlib.Path(".")

        for path, mode, contents in files:
            target = startdir / path
            if writemode == 'overwrite' or not target.exists():
                subprocess.run(f'mkdir -p {target.parent}', shell=True)
                print("DEBUG: Writing:", target)
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
