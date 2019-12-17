#! /usr/bin/env python
"""
Extract Jupyter Notebooks from a Canvas ZIP as HTML.
"""

import shutil
import subprocess
import argparse
import logging
from pathlib import Path

from lifealgorithmic.canvas import Submissions

#logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(
    description="Extract Jupyter notebooks from a Canvas submissions.zip as HTML",
)
parser.add_argument('zip', nargs=1, help='A Canvas submissions.zip')
parser.add_argument('output', nargs=1, help='Output base file.')
parser.add_argument('--users', help='A comma separated list of users.')


def main():
    args = parser.parse_args()

    outfile = Path(args.output[0])
    if outfile.exists():
        raise FileExistsError(outfile)

    users = None
    if args.users is not None:
        users = args.users.split(',')

    subs = Submissions(args.zip[0], users=users)
    for user, path in subs.users():
        for found in path.glob('**/*.ipynb'):
            subprocess.run(f'jupyter nbconvert "{found}"', cwd=path, shell=True, check=True)

    shutil.make_archive(outfile.with_suffix(''), outfile.suffix[1:], subs.workdir())


if __name__ == '__main__':
    main()
