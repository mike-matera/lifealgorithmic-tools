"""
Helpers for a Canvas-based workflow.
"""

import re
import os
import tempfile
import subprocess
import shutil
import filetype
import logging

from pathlib import Path


class Submissions:
    """Work with Canvas' submissions.zip download."""

    def __init__(self, filename, users=None):
        """Extract a submissions.zip and make it ready for use."""

        self.tempdir = tempfile.TemporaryDirectory(prefix='canvas-subs_')
        self._filename = Path(filename).resolve()
        if not self._filename.exists():
            raise FileNotFoundError(filename)

        tempdir = Path(self.tempdir.name)
        self._canvas_temp_dir = tempdir / 'canvas_tmp'
        self._user_temp_dir = tempdir / 'users'
        os.makedirs(self._canvas_temp_dir)
        os.makedirs(self._user_temp_dir)
        subprocess.run(f"unzip '{str(self._filename)}'", cwd=self._canvas_temp_dir, shell=True, check=True,
                       stdout=subprocess.DEVNULL)

        for f in self._canvas_temp_dir.iterdir():
            parts = f.name.split('_')
            user = parts.pop(0)

            if users is not None and user not in users:
                continue

            late = False
            if parts[0] == 'late' or parts[0] == 'LATE':
                late = True
                parts.pop(0)

            while re.match(r'^\d+$', parts[0]) is not None:
                parts.pop(0)

            filename = '_'.join(parts)
            filename = os.path.basename(filename)

            # Fix numbering hassle.
            while re.search(r'-(\d+)\.\w+$', filename) is not None:
                filename = re.sub(r'-\d+\.', '.', filename)

            userdir = self._user_temp_dir / user
            os.makedirs(userdir, exist_ok=True)

            target_file = userdir / filename
            shutil.copy2(f.as_posix(), target_file)
            logging.debug(f"Submitted: {f} -> {target_file}")

            kind = filetype.guess(str(target_file))
            if kind is not None:
                unzipper = None
                if kind.MIME == 'application/zip':
                    unzipper = 'unzip "' + filename + '"'
                elif kind.MIME == 'application/x-tar' or kind.MIME == 'application/gzip' \
                        or kind.MIME == 'application/x-bzip2' or kind.MIME == 'application/x-xz' \
                        or kind.MIME == 'application/x-lzip':
                    unzipper = 'tar -xvf "' + filename + '"'
                elif kind.MIME == 'application/x-7z-compressed':
                    unzipper = '7zr x "' + filename + '"'

                if unzipper is not None:
                    logging.debug(f'unzip: {unzipper}')
                    subprocess.run(unzipper, cwd=userdir, shell=True, check=True, stdout=subprocess.DEVNULL)
                    os.unlink(os.path.join(userdir, filename))
                    # Use chmod to ensure all files are readable. It's possible to zip files that will extract with
                    # permissions that make them unreadable. That's fucked. This fixes it. The "Miguel Ruiz" problem!
                    subprocess.run("chmod -R u+r *", cwd=userdir, shell=True, check=True, stdout=subprocess.DEVNULL)

            if late:
                with open(userdir / '__late__', 'w'):
                    pass

            logging.debug(subprocess.run('tree', cwd=userdir, stdout=subprocess.PIPE).stdout.decode('utf-8'))

    def users(self):
        """Return an iterator that returns:
            - user: The name of the Canvas user
            - path: The path where the submission files are located.
        """
        for path in self._user_temp_dir.iterdir():
            user = path.name
            yield user, path

    def workdir(self):
        """Return the working directory that contains all the user submission directories."""
        return self._user_temp_dir


class Results:
    """Work with results.zip files."""

    def __init__(self, filename, users=None):
        """Extract a results.zip and make it ready for use."""

        self._filename = Path(filename).resolve()
        self._users = users

        if not self._filename.exists():
            raise FileNotFoundError(filename)

        self.tempdir = tempfile.TemporaryDirectory(prefix='canvas-results_')
        subprocess.run(f"unzip '{str(self._filename)}'", cwd=self.tempdir.name, shell=True, check=True,
                       stdout=subprocess.DEVNULL)

    def users(self):
        """Return an iterator that returns:
            - user: The name of the Canvas user
            - path: The path where the submission files are located.
        """
        for path in Path(self.tempdir.name).iterdir():
            user = path.name
            if self._users is None or user in self._users:
                yield user, path

    def workdir(self):
        """Return the working directory that contains all the user submission directories."""
        return Path(self.tempdir.name)
