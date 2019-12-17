import time
import os
import re
import atexit
import subprocess
import hashlib
import urllib.request

score = 0 
total = 100

def get_cfm_number(score) :
    b = bytearray(int(time.time()).to_bytes(8, byteorder='little'))
    b[4] = score & 0xff 
    cfm = int.from_bytes(b, byteorder='big') ^ 0xaa995566deadbeef 
    return cfm;

def print_cfm() :
    global score, total
    print ('Your final score is', score, 'out of', total)
    print ('Your confirmation number is:', get_cfm_number(score))
    print ('''Please enter your confirmation number into Canvas.
You can restart the test any time.\n\n''')

def test_question(points) :
    def _decorator(func) :
        def _wrapper(*args, **kwargs) :
            global score

            print ('-' * 80)
            print (func.__name__, " (", points, " points)\n", sep='')

            try:
                rval = func(*args, **kwargs)
                score += points
                print ('[done]')
                return rval
            except:
                pass
            
            print (func.__doc__)
            print ('Your current score is', score, 'out of', total)
            input ('[Enter to continue.]')
            while True :
                try :
                    rval = func(*args, **kwargs)
                    score += points
                    print ('** Correct **')
                    print ('Congratulations, you have passed this question.')
                    input ('[Enter to continue]')
                    return rval
                except Exception as e :
                    
                    print ('Error:', e)
                    got = input ('Type "skip" to skip the question. Enter to test again: ').strip()
                    if got == 'skip' :
                        print ('Skipping the question.')
                        return None
                    

        return _wrapper
    return _decorator

def capture(cmd, **kwargs) :
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, **kwargs)
    return proc.stdout

@test_question(10)
def set_hostname() :
    '''Configure the host name. 

Change the host name from the default (ubuntu) to anything else. Make sure 
that your change affects the current session and will stay in effect after
a reboot. 
'''

    hostname = capture('hostname').strip()
    assert hostname != 'ubuntu', \
        'The runtime hostname is still set to ubuntu.'

    with open ('/etc/hostname') as h :
        etc_hostname = h.read()

    assert re.match(r'^\s*' + hostname + r'\s*$', etc_hostname), \
        '''The hostname in /etc/hostname doesn't seem to match the current hosname''' 
    
    with open ('/etc/hosts') as h :
        etc_hosts = h.read()

    assert re.search(r'127\.\d+\.\d+\.\d+\s+' + hostname + r'\s', etc_hosts) is not None, \
        '''You have not created an alias for your hostname in /etc/hosts'''

    # Sanity check.
    try :
        ping = capture('ping -q -c 1 -w 1 ' + hostname, check=True)
    except :
        assert False, "Something's wrong. I can't ping your hostname."


@test_question(10)
def do_grub_config() :
    '''Customize GRUB

Change GRUB's configuration to do the following things:

  1. Change the amount of time GRUB spends showing the menu to 10 seconds.
  2. Download the image from the URL below and set it as the GRUB background. 

https://www.cabrillo.edu/services/marketing/images/new_cabrillo_logo_1_003.jpg

'''
    timeout = capture('. /etc/default/grub; echo $GRUB_TIMEOUT')
    try:
        timeout = int(timeout)
    except:
        assert False, '''Oh no! The timeout you entered is not an integer!'''

    assert timeout == 10, \
        '''GRUB's timout has not been set.'''
    
    bg_image = capture('. /etc/default/grub; echo $GRUB_BACKGROUND').strip()
    assert re.match(r'.*\.jpg$', bg_image), \
        '''It doesn't look like you have a background image configured.'''

    assert os.path.isfile(bg_image), \
        '''There's an error in GRUB's configuration. Check your file path.'''

    refhash = '957a16eab6fb035952d2579f6c143c03f20098b74121eb6592af7b6e3c321ba0'
    testhash = hashlib.sha256()
    with open(bg_image, 'rb') as img :
        testhash.update(img.read())

    assert refhash == testhash.hexdigest(), \
        '''You have not used the image I asked for.''' 

    cfg_time = os.path.getmtime('/etc/default/grub')
    bld_time = os.path.getmtime('/boot/grub/grub.cfg')
    assert cfg_time < bld_time, \
        '''You haven't made your made your GRUB changes permanent yet.'''

def get_egg_code():
    ipaddr = subprocess.check_output('ip addr', shell=True).decode('UTF-8')
    m = re.search('link/ether\s+(\S+)', ipaddr)
    mac = m.group(1)
    h = hashlib.md5()
    h.update(b'Salty bo dalty')
    h.update(mac.encode())
    return int.from_bytes(h.digest(), byteorder='big')
    
def loopback_easteregg() :
    fsfile = "/home/student/egg.img"
    egg = get_egg_code()
    if not os.path.isfile(fsfile) :
        try : 
            subprocess.check_call("dd if=/dev/zero of=" + fsfile + " bs=1M count=100", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
            loopdev = subprocess.check_output("losetup -f", shell=True).decode('UTF-8').strip()
            subprocess.check_call('losetup ' + loopdev + ' ' + fsfile, shell=True)
            subprocess.check_call('mkfs.ext4 ' + loopdev, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.check_call('mount ' + loopdev + ' /mnt', shell=True)
            with open('/mnt/egg.txt', 'w') as f : 
                f.write(repr(egg))
                f.write('\n')
            subprocess.check_call('umount ' + loopdev, shell=True)
            subprocess.check_call('losetup -d ' + loopdev, shell=True)
        except Exception as e: 
            print ("INTERNAL ERROR: Fs/File creation failed. Attempting to clean up.")
            subprocess.call('umount ' + loopdev, shell=True)
            subprocess.call('losetup -d ' + loopdev, shell=True)
            os.remove(fsfile)
            raise(e)

@test_question(20)
def mount_egg() :
    '''Mounting a filesystem using a loopback device.

I created a file called egg.img in the current directory. 
The file contains an EXT4 filesystem with an easter egg in it. Mount the 
filesystem in egg.img onto the directory /srv/egg (you will have to create
the directory). 
'''
    mount = capture('mount | grep /srv/egg')
    assert re.search(r'on /srv/egg type ext4', mount), \
        '''You don't seem to have an image mounted on /srv/egg'''
    
    assert os.path.isfile('/srv/egg/egg.txt'), \
        '''I don't see /srv/egg/egg.txt (is the right thing mounted?)'''
    
    expected_code = get_egg_code()
    with open('/srv/egg/egg.txt') as egg :
        found_code = egg.read()

    try:
        found_code = int(found_code.strip())
    except :
        assert False, '''Something is fishy about /srv/egg/egg.txt. This is suspicious.''' 
        
    assert expected_code == found_code, \
        '''The number in /srv/egg/egg.txt doesn't match what I expect. This is suspicous.'''

class lvmdata :
    def load(self, cmd, fields, name) :
        ccmd = cmd + ' -o ' + ','.join(fields) + ' --noheadings --separator : --units b ' + name
        txt = capture(ccmd, check=True)
        data = txt.split(':')
        for idx, field in enumerate(fields) :
            setattr(self, field, data[idx].strip())
        
class VolumeGroup(lvmdata) :
    fields = ['vg_fmt', 'vg_uuid', 'vg_name', 'vg_attr', 'vg_permissions', 'vg_extendable', 'vg_exported', 'vg_partial', 'vg_allocation_policy', 'vg_clustered', 'vg_size', 'vg_free', 'vg_sysid', 'vg_systemid', 'vg_locktype', 'vg_lockargs', 'vg_extent_size', 'vg_extent_count', 'vg_free_count', 'max_lv', 'max_pv', 'pv_count', 'vg_missing_pv_count', 'lv_count', 'snap_count', 'vg_seqno', 'vg_tags', 'vg_profile', 'vg_mda_count', 'vg_mda_used_count', 'vg_mda_free', 'vg_mda_size', 'vg_mda_copies']
    
    def __init__(self, name) :
        try :
            self.load('vgs', VolumeGroup.fields, name)
        except:
            assert False, \
                '''There doesn't appear to be a volume group named ''' + name
            
class LogicalVolume(lvmdata) :
    fields = ['lv_uuid', 'lv_name', 'lv_full_name', 'lv_path', 'lv_dm_path', 'lv_parent', 'lv_layout', 'lv_role', 'lv_initial_image_sync', 'lv_merging', 'lv_converting', 'lv_allocation_policy', 'lv_fixed_minor', 'lv_merge_failed', 'lv_snapshot_invalid', 'lv_when_full', 'lv_active', 'lv_active_locally', 'lv_active_remotely', 'lv_major', 'lv_minor', 'lv_read_ahead', 'lv_size', 'lv_metadata_size', 'seg_count', 'origin', 'origin_uuid', 'origin_size', 'lv_ancestors', 'lv_descendants', 'data_percent', 'snap_percent', 'metadata_percent', 'copy_percent', 'sync_percent', 'raid_mismatch_count', 'raid_write_behind', 'raid_min_recovery_rate', 'move_pv', 'move_pv_uuid', 'convert_lv', 'convert_lv_uuid', 'mirror_log', 'mirror_log_uuid', 'data_lv', 'data_lv_uuid', 'metadata_lv', 'metadata_lv_uuid', 'pool_lv', 'pool_lv_uuid', 'lv_tags', 'lv_profile', 'lv_lockargs', 'lv_time', 'lv_host', 'lv_modules']
    
    def __init__(self, name) :
        try:
            self.load('lvs', LogicalVolume.fields, name)
        except:
            assert False, \
                '''There doesn't appear to be a logical volume named ''' + name

class PhysicalVolume(lvmdata) :
    fields = ['pv_fmt', 'pv_uuid', 'dev_size', 'pv_name', 'pv_mda_free', 'pv_mda_size', 'pe_start', 'pv_size', 'pv_free', 'pv_used', 'pv_attr', 'pv_allocatable', 'pv_exported', 'pv_missing', 'pv_pe_count', 'pv_pe_alloc_count', 'pv_tags', 'pv_mda_count', 'pv_mda_used_count', 'pv_ba_start', 'pv_ba_size', 'vg_name']

    def __init__(self, name) :
        try:
            self.load('pvs', PhysicalVolume.fields, name)
        except Exception as e:
            assert False, \
                '''No physical volume on device ''' + name
        
@test_question(20)
def create_vg() :
    '''Using LVM -- Part 1

Create a volume group called "midterm" using the pysical devices:

  /dev/sdb
  /dev/sdc 
  /dev/sdd

Do not partition the devices first, use the whole disk.
'''    
    vg = VolumeGroup('midterm')
    sdb = PhysicalVolume('/dev/sdb')
    sdc = PhysicalVolume('/dev/sdc')
    sdd = PhysicalVolume('/dev/sdd')

    assert sdb.vg_name == 'midterm', \
        '''/dev/sdb does not belong to the midterm volume group.'''

    assert sdc.vg_name == 'midterm', \
        '''/dev/sdc does not belong to the midterm volume group.'''

    assert sdd.vg_name == 'midterm', \
        '''/dev/sdd does not belong to the midterm volume group.'''

@test_question(10)
def extend_vg() :
    '''Using LVM -- Part 2

Add the following devices to the "midterm" volume group:

  /dev/sde

Do not partition the devices first, use the whole disk.
'''    
    vg = VolumeGroup('midterm')
    sde = PhysicalVolume('/dev/sde')

    assert sde.vg_name == 'midterm', \
        '''/dev/sde does not belong to the midterm volume group.'''

@test_question(20)
def mk_raid_volume() :
    '''Using LVM -- Part 3

Create a RAID 5 logical volume in the midterm volume group. Name the new 
logical volume "data". Allocate 80% of the midterm volume group's physical
extents to the new logical volume.

Format the volume with the EXT4 filesystem and mount it on /srv/data

Hint: The lvcreate command uses logical extents. You will have to do the
conversion from logical to physical extents yourself. 
'''
    vg = VolumeGroup('midterm')
    lv = LogicalVolume('/dev/midterm/data')

    assert re.search('raid5', lv.lv_layout), \
        '''The logical volume /dev/midterm/data isn't RAID 5'''

    vgsize = int(vg.vg_size[0:-1])
    lvsize = (4 * int(lv.lv_size[0:-1])) / 3
    percent = 100 * (lvsize / vgsize)
    
    assert percent > 70 and percent < 90, \
        'The logical volume is using {}% of the volume group. Try again'.format(int(percent))

    mount = capture('mount | grep /srv/data')
    assert re.search(r'data on /srv/data type ext4', mount), \
        '''/srv/data is not mounted or the wrong filesystem type.'''


@test_question(10)
def mk_snapshot_volume() :
    '''Using LVM -- Part 4

Using the remaining space in your "midterm" volume group create a snapshot
logical volume named "snap". 

Mount the snapshot on /srv/snap
'''
    vg = VolumeGroup('midterm')
    lv = LogicalVolume('/dev/midterm/snap')

    assert re.search('snapshot', lv.lv_role), \
        '''The logical volume /dev/midterm/snap isn't a snapshot!'''
    
    assert lv.origin == 'data', \
        '''The logical volume /dev/midterm/snap isn't a snapshot of the data LV!'''

    mount = capture('mount | grep /srv/snap')
    assert re.search(r'snap on /srv/snap type ext4', mount), \
        '''/srv/snap is not mounted or the wrong filesystem type.'''
        
def main() :
    '''
** Welcome to the CIS-191 midterm for fall 2017 ** 

I will ask you to make configuration changes to your VM. After I ask each 
question I will test to see if your configuration is correct. If not I'll 
give you an error message and ask if you want to test the configuration again 
or skip the question. 

When the midterm exits it will print a confirmation number. Copy and paste the
number into Canvas. Be careful to get the number exactly! You can stop the 
midterm program and restart it at any time. But, Canvas is timing you so you
must finish in the allotted time. 
'''
    assert os.geteuid() == 0, "You must be root to when you run this test."

    atexit.register(print_cfm)
    print (main.__doc__)
    input ('[Enter to continue.]')

    # The test
    set_hostname()
    do_grub_config()

    # Create the easter egg.
    loopback_easteregg()

    # Mount the easter egg
    mount_egg()

    create_vg()
    extend_vg()
    mk_raid_volume()
    mk_snapshot_volume()

    print ('\n\n', '*' * 80, sep='')
    print ('\nCongratulations, you have finished the test.\nI hope you enjoyed it.\n\n')
    
if __name__ == '__main__' :
    main()
