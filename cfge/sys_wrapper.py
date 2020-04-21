import os
import sys
import tempfile
import shutil
import atexit 
import sqlite3
import subprocess
import random 
import pickle

class RealSystem :
    def __init__(self, wd) :
        # initialize db

        # make temporary
        self.workdir = wd

        # copy infrastructure
        #pkgdir = os.path.abspath(__package__)
        #shutil.copytree(pkgdir, self.workdir + "/cfge", ignore=shutil.ignore_patterns('__pycache__'))

        #mainscript = os.path.abspath(sys.argv[0])
        #shutil.copy(mainscript, self.workdir + "/__main__.py")

        #self.dbpath = self.workdir + 'resources.db'
        self.db = sqlite3.connect(":memory:")
        print("no resources, do it live!")
        c = self.db.cursor()
        c.execute('''create table meta (key text, value text)''')
        c.execute('''create table blobs (id integer primary key, ref text, data blob, flags integer)''')
        self.db.commit()

    def __del__(self) :
        self.db.close()

    def readfile(self, path) :
        f = open(path, 'r') 
        data = f.read()
        f.close()
        self.set_blob(path, data)
        return data
        
    def check_output(self, cmd) :
        cmdstring = ' '.join(cmd)
        output = subprocess.check_output(cmd)
        self.set_blob(cmdstring, output)
        return output
        
    def geteuid(self) : 
        euid = os.geteuid()
        self.set_meta('euid', euid)
        return euid

    def persist(self, filename) :    
        print ("persist!")
        #shutil.make_archive(filename, 'zip', self.workdir)

    def input(self) : 
        got = input()
        self.set_blob('stdin', got, 0)
        return got

    def seed(self) : 
        s = os.urandom(8)
        self.set_meta('seed', s)
        random.seed(s)

    def getpid(self) :
        pid = os.getpid()
        self.set_meta('pid', pid)
        return pid 

    def listdir(self, path) :
        contents = os.listdir(path)
        self.set_blob(path, pickle.dumps(contents), 0)
        return contents 

    def readlink(self, path) :
        l = os.readlink(path)
        self.set_blob(path, l, 0)
        return l

    def set_blob(self, ref, data, flags=0) :
        c = self.db.cursor()
        c.execute('''insert into blobs values (NULL, ?, ?, ?)''', [ref, data, flags])
        self.db.commit()

    def set_meta(self, key, value) :
        c = self.db.cursor()
        c.execute('''insert into meta values (?, ?)''', [key, value])
        self.db.commit()

