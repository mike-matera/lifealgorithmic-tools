"""
The CIS-191 final for Spring 2019
"""

import os
import re
import tempfile
import subprocess
import pwd
import hmac
import crypt
import sys
import random
import datetime
import collections

from pathlib import Path

from lifealgorithmic.linux.test import LinuxTest
from lifealgorithmic.linux.disks import VolumeGroup, PhysicalVolume, LogicalVolume, capture

test = LinuxTest("This is the secret. Don't tell anyone")


@test.question(10, to='finalsp19')
def set_hostname(to):
    """Configure the host name.

Change the host name from the default to '{to}'.

Make sure that your change affects the current session and will stay in effect after a
reboot of the VM.
"""

    hostname = capture('hostname').strip()
    assert hostname == to, \
        'The runtime hostname is not set properly.'

    with open('/etc/hostname') as h:
        etc_hostname = h.read()

    assert re.match(r'^\s*' + hostname + r'\s*$', etc_hostname), \
        '''The hostname in /etc/hostname doesn't seem to match the current hostname'''

    with open('/etc/hosts') as h:
        etc_hosts = h.read()

    assert re.search(r'127\.\d+\.\d+\.\d+\s+' + hostname + r'\s', etc_hosts) is not None, \
        '''You have not created an alias for your hostname in /etc/hosts'''

    # Sanity check.
    try:
        ping = capture('ping -q -c 1 -w 1 ' + hostname, check=True)
    except:
        assert False, "Something's wrong. I can't ping your hostname."


@test.question(10)
def do_grub_config():
    '''Customize the Kernel Command Line

Use GRUB to customize the kernel command line. Add the parameter "cis191=true"
to the kernel command line options. Reboot the VM to complete the process and
restart the test.
'''
    with open('/proc/cmdline') as f:
        cmdline = f.read()

    if re.search(r'cis191=true', cmdline) is None:
        assert False, """The kernel command line doesn't have cis191=true in it."""


@test.question(10, vgname="final", devices=['/dev/sdc', '/dev/sdd', '/dev/sde'])
def create_vg(vgname, devices):
    '''Using LVM -- Create a Volume Group

Create a volume group called "{vgname}" using the physical devices:

  {devices}

Do not partition the devices first, use the whole disk.
'''

    disks = [Path(x) for x in devices]

    vg = VolumeGroup(vgname)
    pvs = [PhysicalVolume(str(x)) for x in disks]

    for x in range(len(disks)):
        assert pvs[x].vg_name == vgname, \
            '''{} does not belong to the {} volume group.'''.format(str(disks[x]), vgname)


@test.question(10, vgname="final", lvname="data", mountpoint="/srv/data")
def mk_raid5_volume(vgname, lvname, mountpoint):
    '''Using LVM -- Part 2

Create a RAID 5 logical volume in the {vgname} volume group. Name the new
logical volume "{lvname}". Allocate 100% of the {vgname} volume group's physical
extents to the new logical volume.

Format the volume with the EXT4 filesystem and mount it on {mountpoint}
'''
    vg = VolumeGroup(vgname)
    lv = LogicalVolume('/dev/{}/{}'.format(vgname, lvname))

    assert re.search('raid5', lv.lv_layout), \
        '''The logical volume isn't RAID 5'''

    assert int(vg.vg_free_count) == 0, """There are free extents in the volume group."""

    mount = capture('mount | grep {}'.format(mountpoint))
    assert re.search(r'data on {} type ext4'.format(mountpoint), mount), \
        '''{} is not mounted or the wrong filesystem type.'''.format(mountpoint)


@test.question(10, username="datauser", homedir="/srv/data", password="changeme", userid=3000)
def test_add_user(username, homedir, password, userid):
    '''Create a user named "{username}" with the following properties:

    User ID: {userid}
    Home directory: {homedir}
    Password: {password}

Set the user's password to expired so that they must change their password
the next time they login.
'''
    try:
        sysuser = pwd.getpwnam(username)
    except:
        assert False, "You don't seem to have created the user."

    assert sysuser[2] == userid, "Oops. The userid isn't correct"
    assert sysuser[5] == homedir, "Oops. The user doesn't have the correct home directory"

    with open('/etc/shadow', 'r') as sh:
        for shuser in sh.readlines():
            sysshadow = shuser.strip().split(':')
            if sysshadow[0] == username:
                break

    pwhash = sysshadow[1].split('$', 3)
    assert hmac.compare_digest(crypt.crypt(password, salt="$" + pwhash[1] + "$" + pwhash[2]),
                               sysshadow[1]), "Oops. The password doesn't match"

    assert int(sysshadow[2]) == 0, "Oops. The user's password is not set to expired."


@test.question(10)
def use_tar():
    """Use TAR to make a backup of the /etc directory. Place the backup in the file ~/etc_backup.tar"""

    p = Path(os.environ['HOME']) / 'etc_backup.tar'
    assert p.exists(), """I can't find ~/etc_backup.tar"""

    # Get the contents
    try:
        dir = capture("tar -tvf {}".format(p))
    except:
        assert False, """I was not able to analyze your TAR file. Check the file type."""

    # Validate
    with tempfile.TemporaryDirectory() as d:
        subprocess.run('tar -cf expect.tar /etc', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=d)
        exp = capture("tar -tvf expect.tar", cwd=d)

    dir = dir.split('\n')
    exp = exp.split('\n')

    if len(dir) != len(exp):
        assert False, """The contents of your TAR file don't match the contents of /etc (wrong number of files.)"""

    for i in range(len(exp)):
        if exp[i] != dir[i]:
            assert False, """The contents of the TAR file don't match /etc:
Your file:
{}
Expected:
{}
""".format(dir[i], exp[i])


def ps(filter=None):
    output = capture('ps -elf').split('\n')[1:-1]
    for line in output:
        data = line.split(sep=None, maxsplit=14)
        proc = {
            'f': data[0],
            's': data[1],
            'uid': data[2],
            'pid': int(data[3]),
            'ppid': int(data[4]),
            'c': data[5],
            'pri': int(data[6]),
            'ni': data[7],
            'addr': data[8],
            'sz': int(data[9]),
            'wchan': data[10],
            'stime': data[11],
            'tty': data[12],
            'time': data[13],
            'cmd': data[14],
        }
        if filter is None or filter(proc):
            yield proc


@test.question(10)
def memory_for_process():
    """Finding Processes
"""
    if sys.stdin == None:
        raise RuntimeError

    counts = collections.Counter(x['cmd'] for x in ps())
    cands = ps(filter=lambda x: counts[x['cmd']] == 1 and not x['cmd'].startswith('['))
    proc = random.choice(list(cands))
    print("""Find a process that is running the following command:

    {cmd}

""".format(cmd=proc['cmd']))

    if test.debug:
        print('DEBUG:', proc['sz'])
    try:
        got = int(test.input('How much memory is the process using in KB? '))
    except:
        got = 0

    assert got == proc['sz'], \
        """The memory size of the process doesn't match what I expected. ({})""".format(proc['sz'])


@test.question(10)
def stderr_for_process():
    """Finding Processes
"""
    if sys.stdin == None:
        raise RuntimeError

    def filter_on_stderr(proc):
        p = Path("/proc/{}/fd/2".format(proc['pid']))
        try:
            return p.resolve().exists()
        except:
            return False

    cands = ps(filter=filter_on_stderr)
    proc = random.choice(list(cands))
    print("""Find a process that is running the following command:

    {cmd}

""".format(cmd=proc['cmd']))

    stderr = Path("/proc/{}/fd/2".format(proc['pid'])).resolve()
    if test.debug:
        print('DEBUG:', stderr)
    got = test.input('What is STDERR for this process? ').strip()
    assert got == str(stderr), \
        """The file doesn't match what I expected. ({})""".format(stderr)


@test.question(10)
def renice_process():
    """Finding Processes
"""
    if sys.stdin == None:
        raise RuntimeError

    counts = collections.Counter(x['cmd'] for x in ps())
    cands = ps(filter=lambda x: counts[x['cmd']] == 1 and not x['cmd'].startswith('['))
    proc = random.choice(list(cands))
    print("""Find a process that is running the following command:

    {cmd}

Renice the process to a niceness of 12.
""".format(cmd=proc['cmd']))

    if test.debug:
        print('DEBUG:', proc['pid'])
    test.input('[Enter to Continue] ')

    regot = list(ps(filter=lambda x: x['pid'] == proc['pid']))[0]
    assert int(regot['ni']) == 12, \
        """The niceness match what I expected."""


@test.question(10)
def find_open_file():
    """Find an open file.

I have opened a random temporary file. What is the full path of the file?

Hint: I've hidden the file by deleteing it.
"""
    with tempfile.NamedTemporaryFile(delete=False) as randfile:
        os.unlink(randfile.name)
        if test.debug:
            print("DEBUG:", randfile.name)
        ans = test.input('Enter the file name: ').strip()
        assert ans == str(randfile.name), "Oops. That's not correct."


def main():
    """
** Welcome to the CIS-191 final for spring 2019 **

I will ask you to make configuration changes to your VM. After I ask each
question I will test to see if your configuration is correct. If not I'll
give you an error message and ask if you want to test the configuration again
or skip the question.

When the final exits it will print a confirmation number. Copy and paste the
number into Canvas. Be careful to get the number exactly! You can stop the
final program and restart it at any time. But, Canvas is timing you so you
must finish in the allotted time.
"""
    print(main.__doc__)

    test.run(debug=False)

    print("All done!\n\n")

if __name__ == '__main__':
    main()

