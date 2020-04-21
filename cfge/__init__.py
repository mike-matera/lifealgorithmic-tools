import os
import shutil
import atexit 
import tempfile 
from cfge import sys_wrapper
from cfge import db_wrapper


# Create a temp directory 
__workdir = tempfile.mkdtemp()

@atexit.register
def __cleanup() :
    shutil.rmtree(__workdir)

def instance() :
    global __instance
    if not '__instance' in globals() :
        try :
            dbdata = __loader__.get_data(os.path.join('cfge','resources.db'))
            __instance = db_wrapper.DBSystem(__workdir)
            __instance.seed()

        except FileNotFoundError :
            __instance = sys_wrapper.RealSystem(__workdir)
            __instance.seed()

    return __instance
