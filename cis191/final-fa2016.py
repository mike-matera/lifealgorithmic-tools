#! /usr/bin/python3 

import sys 
import os 
import time 
import subprocess 
import random 
import re
import traceback 
import hashlib 
import tempfile
import crypt
import pwd
import hmac
import signal
import atexit

# Ideas... 
#  # Create a loopback device, format and mount it. 
#  Add a user, set some key attributes. 
#  Find and guess process metrics (memory, runtime, etc). 
#  x Install/remove software. 
#  boot custom kernel?  coule reuse existing compile dir. 
#  x Determine what modules are installed, what they depend on... 
#  x Check for a package wiht apt-cache search 
#  x Check what package a file belongs to. 
#  Use find to find something... 

debug = False
score = 0
total = 100
usr_files = subprocess.check_output(['find /usr/bin'], shell=True).split()

def install_software() :
    '''Software installation'''
    print ("Install the Multiple Arcade Machine Emulator package.")
    try :
        subprocess.check_call(['dpkg -l mame'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except : 
        assert False, "The package is not installed."

def first_blk_uuid() :
    '''Working with block devices, UUIDs and filesystems'''
    blkid = subprocess.check_output(['blkid'], shell=True).decode('UTF-8').split()
    bd = blkid[0][:-1]
    uuid = blkid[1][6:-1].lower()
    fs = blkid[2][6:-1].lower()
    if debug : 
        print ("DEBUG:", bd, uuid, fs)
    print ("What type of filesystem is mounted on " + bd + "?")
    ans = sys.stdin.readline().strip().lower()
    assert ans == fs, "That's not the right type of filesystem."
    print ("What is the UUID of the filesystem is mounted on " + bd + "?")
    print ("(Answer is not case-sensitive.)")
    ans = sys.stdin.readline().strip().lower()
    assert ans == uuid, "That's the wrong UUID."

def load_meminfo() :
    meminfo = {}
    with open('/proc/meminfo', 'r') as mi : 
        for line in mi : 
            m = re.match('(\S+):\s+(\d+)\s+(\S+)', line)
            if m is not None : 
                meminfo[m.group(1)] = m.group(2)
    return meminfo 

def identify_all_memory() :
    '''Checking memory'''
    meminfo = load_meminfo()
    if debug : 
        print ("DEBUG:", meminfo['MemTotal'])
    print ("How much memory is installed in this system in kilobytes?")
    ans = sys.stdin.readline().strip()
    assert meminfo['MemTotal'] == ans, "That's not the correct amount of installed memory."

def identify_free_memory() :
    '''Free memeory'''
    meminfo = load_meminfo()
    if debug : 
        print ("DEBUG:", meminfo['MemFree'])
    print ("How much memory is free in kilobytes (answer must be within 1MiB)?")
    ans = int(sys.stdin.readline().strip())
    meminfo = load_meminfo()
    assert int(meminfo['MemFree']) < ans + 1024 and int(meminfo['MemFree']) > ans - 1024, "That's not the correct amount of free memory.\nThe amount may have changed since you checked it).\nTry again."
    
def identify_file_package() :
    '''Packages and installed files.'''
    package = None
    while package is None :
        try :
            f = usr_files[random.randint(0, len(usr_files)-1)].decode('UTF-8')
            dpkg = subprocess.check_output(["dpkg -S " + f], shell=True).decode('UTF-8').strip()
            m = re.match("(\S+):\s+(\S+)", dpkg)
            if m is not None :
                package = m.group(1)
                if debug : 
                    print ("DEBUG: ", package)
        except Exception as e: 
            return
                    
    print ("What package does the file", f, "belong to?")
    ans = sys.stdin.readline().strip()
    assert package == ans, "Sorry, that's not the correct package."

def count_block_devices() :
    '''Finding things.'''
    print ("How many block devices are in the /dev directory?")
    f = int(subprocess.check_output(['find /dev -type b | wc -l'], shell=True).strip())
    ans = int(sys.stdin.readline().strip())
    if debug : 
        print ("DEBUG:", f)
    assert f == ans, "That's the wrong answer!"
        
def get_cfm_number(score) :
    b = bytearray(int(time.time()).to_bytes(8, byteorder='little'))
    b[4] = score & 0xff 
    cfm = int.from_bytes(b, byteorder='big') ^ 0xaa995566deadbeef 
    return cfm;

def correct(s) : 
    global score
    score += s
    print ("Correct! Your score is now", score, "out of", total)

def loop_filesystem() :
    loopfile = 'loop.img'
    loopdev = '/dev/loop0'
    mountpoint = '/mnt/final'

    if not os.path.isfile(loopfile) :
        subprocess.check_call("dd if=/dev/zero of=" + loopfile + " bs=1M count=500", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print ("I have just made a file called", loopfile, "in the current directory.")      

    print ("Bind the file to the loopback device", loopdev)
    losetup = subprocess.check_output("losetup -j " + loopfile, shell=True).decode('UTF-8').strip()
    assert loopdev == losetup.split(':')[0], "Oops. I can't find a loop device associated with the file."    
    
    print ("Now format the loopback device with the ext4 filesystem.") 
    blkid = subprocess.check_output("blkid -p " + loopdev, shell=True).decode('UTF-8').strip()
    m = re.search('/dev/loop0: UUID="([^"]+)".*TYPE="ext4"', blkid)
    assert m is not None, "Oops. I don't see any filesystem on " + loopdev
    uuid = m.group(1)
    print ("I found a filesystem with UUID", uuid)
    print ("Mount it on", mountpoint)
    mount = ""
    with open('/proc/mounts', 'r') as mounts :
        for m in mounts : 
            mm = m.split()
            if mm[0] == '/dev/loop0' :
                mount = mm[1]
    assert mount == mountpoint, "Ooops. It doesn't look like you have the filesystem mounted."

def loopback_easteregg() :
    '''Loopback devices and mount'''
    fsfile = "egg.img"
    ipaddr = subprocess.check_output('ip addr', shell=True).decode('UTF-8')
    m = re.search('link/ether\s+(\S+)', ipaddr)
    mac = m.group(1)
    h = hashlib.md5()
    h.update(b'This is some salt')
    h.update(mac.encode())
    egg = int.from_bytes(h.digest(), byteorder='big')
    if not os.path.isfile(fsfile) :
        try : 
            subprocess.check_call("dd if=/dev/zero of=" + fsfile + " bs=1M count=100", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
            loopdev = subprocess.check_output("losetup -f", shell=True).decode('UTF-8').strip()
            subprocess.check_call('losetup ' + loopdev + ' ' + fsfile, shell=True)
            subprocess.check_call('mkfs.ext4 ' + loopdev, shell=True)
            subprocess.check_call('mount ' + loopdev + ' /mnt', shell=True)
            with open('/mnt/egg.txt', 'w') as f : 
                f.write(repr(egg))
                f.write('\n')
            subprocess.check_call('umount ' + loopdev, shell=True)
            subprocess.check_call('losetup -d ' + loopdev, shell=True)
            print ("I just created a file called egg.txt in an ext4 filesystem containes in the file", fsfile)
        except Exception as e: 
            print ("INTERNAL ERROR: Fs/File creation failed. Attempting to clean up.")
            subprocess.call('umount ' + loopdev, shell=True)
            subprocess.call('losetup -d ' + loopdev, shell=True)
            os.remove(fsfile)
            raise(e)

    print ("Mount the", fsfile, "using a looback device and tell me what's hidden inside.")
    if debug : 
        print ("DEBUG:", egg)
    ans = sys.stdin.readline().strip()
    assert ans == str(egg), "Oops. That's not the right answer. Please try again."

def check_modules() :
    '''Kernel modules'''
    modules = []
    with open('/proc/modules', 'r') as m :
        for mod in m.readlines() :
            modules.append(mod.split())

    candidates = []
    for mod in modules :
        deps = mod[3].split(',')
        if deps[0] != '-' and len(deps) == 2 :
            candidate = []
            candidate.append(mod[0])
            candidate.append(deps[0])
            candidates.append(candidate)
            
    modnumber = random.randint(0, len(candidates)-1)
    module = candidates[modnumber][0]
    moduledep = candidates[modnumber][1]
    assert module is not None, "Internal Error: I couldn't find a module to ask about!"
    if debug :
        print ("DEBUG:", moduledep)
    print ("What module(s) does the module named \"" + module + "\" depend on?")
    ans = sys.stdin.readline().strip()
    assert ans == moduledep, "Oops. That's not correct."

def find_open_file() :
    '''Examining processes and file descriptors'''
    with tempfile.TemporaryFile() as randfile :
        link = os.path.join(os.sep, 'proc', 'self', 'fd', str(randfile.name))
        target = os.readlink(link).split()[0]        
        if debug :
            print ("DEBUG:", target)
        print ("I have opened a random temporary file. What is the full path of the file?")
        print ("Hint: I've hidden the file by deleteing it.")
        ans = sys.stdin.readline().strip()
        assert ans == str(target), "Oops. That's not correct."

def test_add_user() :
    username = 'finaluser'
    homedir = '/home/' + username
    password = '12345'
    userid = 6789
    expdate = 17167
    
    print ("Create a user named", username, "with the following properties:")
    print ("\tUser ID:", userid)
    print ("\tHome directory:", homedir)
    print ("\tPassword:", password, "(expires on the next login)")
    print ("\tAccount expires on 1/1/2017")

    sysuser = pwd.getpwnam(username)
    assert sysuser[2] == userid, "Oops. The userid isn't correct"
    assert sysuser[5] == homedir, "Oops. The user doesn't have the correct home directory"

    with open('/etc/shadow', 'r') as sh :
        for shuser in sh.readlines() :
            sysshadow = shuser.strip().split(':')
            if sysshadow[0] == username :
                break
    
    pwhash = sysshadow[1].split('$', 3)    
    assert hmac.compare_digest(crypt.crypt(password, salt="$"+pwhash[1]+"$"+pwhash[2]), sysshadow[1]), "Oops. The password doesn't match"

    assert int(sysshadow[2]) == 0, "Oops. The user's password is not set to expired."
    assert sysshadow[7] != '' and int(sysshadow[7]) == expdate, "Ooops. The user's account doesn't expire on the correct date."

def testquestion(func, points) :
    print ("\n\n*")
    print ("*", func.__doc__)
    print ("* (" + str(points) + " points)")
    print ("*")
    while True :
        try :
            func()
            correct(points)
            return
        except Exception as e :
            print ("ERROR:", e)
            if debug : 
                print ("Error was", repr(e))
        print ("Would you like to retry this question? [yes/no]")
        rt = sys.stdin.readline().strip()
        while rt != 'yes' and rt != 'no' :
            print ("Please type 'yes' or 'no'")
            rt = sys.stdin.readline().strip()
        if rt == 'no' :
            return

def int_handler(signum, frame) :
    print ("Exiting because of CTRL-C")
    exit(-signum)
    
def print_cfm() :
    print ("Your score is:", score, "out of", total)
    print ("Your confirmation number is:", get_cfm_number(score), " please submit it on Canvas.")
    
def main() :
    random.seed()
    signal.signal(signal.SIGINT, int_handler)
    
    print ("*\n*\n*")
    print ("** Welcome to the CIS-191 final.")
    print ("*\n*\n*")

    try:
        assert os.geteuid() == 0, "You must be root to when you run this test."

        atexit.register(print_cfm)
        testquestion(count_block_devices, 5)
        testquestion(identify_file_package, 5) 
        testquestion(identify_all_memory, 5)
        testquestion(identify_free_memory, 5)
        testquestion(first_blk_uuid, 15)
        testquestion(install_software, 15)
        testquestion(loopback_easteregg, 25)
        testquestion(check_modules, 10)
        testquestion(find_open_file, 10)
        testquestion(test_add_user, 15)
        
    except Exception as e :
        print ("ERROR:", e)
        if debug : 
            print ("Error was", repr(e))



if __name__ == "__main__": 
    main()
