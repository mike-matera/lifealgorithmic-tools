import os
import sys
import sqlite3
import atexit
import tempfile 
import zipimport 
import random 
import pickle 

class DBSystem :

    def __init__(self, wd) :
        # initialize db
        print("using db")
        print ("debug:", __file__)
        
        # make temporary
        self.workdir = wd
        dbpath = self.workdir + '/resources.db'
        dbdata = __loader__.get_data(os.path.join('cfge','resources.db'))
        dbfile = open(dbpath, 'wb')
        dbfile.write(dbdata)
        dbfile.close()
        self.db = sqlite3.connect(dbpath)
        self.ref_num = 1

    def __del__(self) :
        self.db.close()

    def readfile(self, path) :
        return self.get_blob(path)[0]
                
    def check_output(self, cmd) :
        return self.get_blob(' '.join(cmd))[0]

    def geteuid(self) : 
        return int(self.get_meta('euid'))

    def input(self) : 
        return self.get_blob('stdin')[0]

    def persist(self, filename) :    
        print ("db was persisted at this point.")

    def seed(self) : 
        s = self.get_meta('seed')
        random.seed(s)

    def getpid(self) :
        return self.get_meta('pid')

    def listdir(self, path) :
        return pickle.loads(self.get_blob(path)[0]);

    def readlink(self, path) :
        return self.get_blob(path)[0]

    def get_blob(self, ref) :
        c = self.db.cursor()
        c.execute('''select data, flags from blobs where id==? and ref==?''', \
                  [self.ref_num, ref])
        row = c.fetchone()
        self.ref_num += 1
        return [row[0], row[1]]
        
    def get_meta(self, key) :
        c = self.db.cursor()
        c.execute('''select value from meta where key==?''', [key])
        return c.fetchone()[0]
