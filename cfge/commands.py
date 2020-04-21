
import cfge
import re

def mounts() : 
    out = cfge.instance().check_output(["mount"])
    mnt = {}
    mnt['by_device'] = {}
    mnt['by_mount'] = {}
    for line in out.splitlines(True) : 
        s = line.split()
        mnt['by_device'][s[0].decode()] = s[2].decode()
        mnt['by_mount'][s[2].decode()] = s[0].decode()
    return mnt;

def readtab(cmd, idcol=0, headers=None, sep=None) :
    r = {}
    out = cfge.instance().check_output(cmd).splitlines(True)

    if headers == None:
        headers = out[0].decode().split(sep=sep)

    for line in out[1:] :
        data = line.decode().split(sep=sep, maxsplit=len(headers)-1)
        key = data[idcol].lower().strip()
        r[key] = {}
        for index, item in enumerate(data) :
            r[key][headers[index].lower().strip()] = item.strip()

    return r

def ps() :
    return readtab(cmd=['ps', '-elfy'], idcol=2)

def lvmstat() :
    r = {}
    r['lvs'] = readtab(cmd=['lvs', '-o', 'lv_all,vg_all', '--separator', '!:!'], sep='!:!')
    r['vgs'] = readtab(cmd=['vgs', '-o', 'vg_all', '--separator', '!:!'], sep='!:!', idcol=2)
    r['pvs'] = readtab(cmd=['pvs', '-o', 'pv_all', '--separator', '!:!'], sep='!:!', idcol=3)
    # add some helpful info to lvs output 
    for lv in r['lvs'].values() : 
        lv['mountpath'] = "/dev/mapper/" \
                         + re.sub('-', '--', lv['vg']) \
                         + "-" + re.sub('-', '--', lv['lv'])

    return r
