"""
Module with helpers for Linux tests.
"""

import re
import os
import sys
import time
import atexit
import hashlib
import subprocess
import tempfile
import pathlib
import traceback


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

    def __init__(self, secret):
        self.score = 0
        self.total = 0
        self.secret = secret
        self.debug = False
        self.questions = []

    def get_cfm_number(self):
        secret_hash = hashlib.sha256()
        secret_hash.update(self.secret.encode('utf-8'))
        key = int.from_bytes(secret_hash.digest(), byteorder='little') & 0xffffffffffffffff
        b = bytearray(int(time.time()).to_bytes(8, byteorder='little'))
        b[4] = self.score & 0xff
        for bb in b[0:7]:
            b[7] = b[7] ^ bb
        cfm = int.from_bytes(b, byteorder='big') ^ key
        return cfm

    def print_cfm(self):
        print (Formatting.Bold, end='')
        print('Your final score is', self.score, 'out of', self.total)
        print('Your confirmation number is:', self.get_cfm_number())
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

    def input(self, prompt):
        return input(Color.F_LightYellow + prompt + Color.F_Default)

    def print_error(self, *stuff):
        print(Color.F_LightRed, end='')
        print(*stuff)
        print(Color.F_Default, end='')

    def print_success(self, *stuff):
        print(Color.F_LightGreen, end='')
        print(*stuff)
        print(Color.F_Default, end='')

    def question(self, points, setup=None, **decorator_kwargs):
        def _decorator(func):
            def _wrapper():

                if setup is not None:
                    setup()

                print(Formatting.Bold, end='')
                print('-' * 80)
                print(func.__name__, " (", points, " points)\n", sep='')
                print(Formatting.Reset, end='')

                interactive = False
                old_stdin = sys.stdin
                sys.stdin = None
                try:
                    rval = func(**decorator_kwargs)
                    self.score += points
                    self.print_success('[done]')
                    return rval
                except RuntimeError:
                    interactive = True
                except Exception as e:
                    if self.debug:
                        self.print_error('Dry run caused an error:', e)
                finally:
                    sys.stdin = old_stdin

                print(_wrapper.__doc__)

                if not interactive:
                    print(Color.F_LightGreen + 'Your current score is', self.score, 'out of', self.total, Color.F_Default)
                    self.input('[Enter to continue.]')

                while True:
                    try:
                        rval = func(**decorator_kwargs)
                        self.score += points
                        self.print_success('** Correct **')
                        self.input('[Enter to continue]')
                        return rval
                    except Exception as e:
                        self.print_error('Error:', e)
                        if self.debug:
                            traceback.print_exc()

                        got = self.input('Type "skip" to skip the question. Enter to test again: ').strip()
                        if got == 'skip':
                            print('Skipping the question.')
                            return None

            # Expose docstring to the wrapped function.
            _wrapper.__doc__ = func.__doc__.format(**decorator_kwargs)
            _wrapper.__name__ = func.__name__
            self.questions.append(_wrapper)
            if self.total > -1:
                self.total += points

            return _wrapper

        return _decorator

    def run(self, debug=False, skip=[], only=None):
        """Run the test.

            debug - Enable debugging. Reveals answers to interactive questions.
            skip - A list of tests to skip.
            only - A list of tests to run.

        """
        self.debug = debug
        #assert os.geteuid() == 0, "You must be root to when you run this test."
        atexit.register(self.print_cfm)

        self.input('[Enter to start the test]')
        for q in self.questions:
            if q.__name__ not in skip and (only is None or q.__name__ in only):
                q()
