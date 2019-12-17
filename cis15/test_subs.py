#! /usr/bin/env python
"""
Run a Python test class against a Canvas submissions.zip
"""

import os
import shutil
import subprocess
import argparse
import logging
from pathlib import Path

from lifealgorithmic.canvas import Submissions

if 'GRADER_DEBUG' in os.environ:
    logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(
    description="Run a Python test class against a Canvas submissions.zip",
)
parser.add_argument('test', nargs=1, help='A Python test program')
parser.add_argument('zip', nargs=1, help='A Canvas submissions.zip')
parser.add_argument('output', nargs=1, help='Output base file')
parser.add_argument('--users', help='A comma separated list of users')


def main():
    args = parser.parse_args()

    outfile = Path(args.output[0])
    if outfile.exists():
        raise FileExistsError(outfile)

    users = None
    if args.users is not None:
        users = args.users.split(',')

    test = args.test[0]
    subs = Submissions(args.zip[0], users=users)
    for user, path in subs.users():
        print(f'Working on user: {user}')
        result = subprocess.run(f'python -m "{test}"', cwd=path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=True, check=False, encoding='utf-8')
        files = subprocess.run('tree', cwd=path, stdout=subprocess.PIPE, encoding='utf-8')
        logging.debug(files.stdout)
        logging.debug(result.stdout)
        with open(path / 'comments.log', 'w') as log:
            log.write(f"""
Hello {user}!

I'm a robot that tests your program.
Mike writes a bunch of tests and I run them to see if your
program meets all of the specified requirements. Mike decides
your final grade. Robots aren't good at that kind of thing.

Here are the files I'm returning to you':
----------------------------------------------------------------------
""")
            log.write(files.stdout)
            log.write("""

Here are your results:
----------------------------------------------------------------------
""")
            log.write(result.stdout)

    shutil.make_archive(outfile.with_suffix(''), outfile.suffix[1:], subs.workdir())


if __name__ == '__main__':
    main()
