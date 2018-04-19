
"""
    :created: 11.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""


import os
import shutil
import tempfile
from pathlib import Path

# Bootstrap-Env
import bootstrap_env
from bootstrap_env.admin_shell.path_helper import PathHelper


base_file = bootstrap_env.__file__
print("\nbootstrap_env.__file__: %r\n" % base_file)

path_helper = PathHelper(
    base_file=base_file,
    boot_filename="boot_bootstrap_env.py",
    admin_filename="bootstrap_env_admin.py",
)
path_helper.print_path()
path_helper.assert_all_path()


class IsolatedFilesystem:
    """
    Context manager, e.g.:

    with isolated_filesystem(prefix="temp_dir_prefix"):
        print("I'm in the temp path here: %s" % Path().cwd())
    """
    def __init__(self, prefix=None):
        super().__init__()

        self.prefix = prefix

    def __enter__(self):
        print("Use prefix: %r" % self.prefix)

        self.cwd = Path().cwd()
        self.temp_path = tempfile.mkdtemp(prefix=self.prefix)
        os.chdir(self.temp_path)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(str(self.cwd)) # str() needed for older python <=3.5
        try:
            shutil.rmtree(self.temp_path)
        except (OSError, IOError):
            pass
