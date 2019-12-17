#! /usr/bin/env python3

import os
import time
import random
import tempfile

def main():

    files = []
    for _ in range(random.randint(10, 20)):
        files.append(tempfile.TemporaryFile())

    while True:
        stuff = os.urandom(1024*1042*256)
        time.sleep(1)


if __name__ == '__main__':
    main()