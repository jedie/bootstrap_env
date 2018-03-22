
"""
    :created: 11.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""


import os
import subprocess
import unittest
from pathlib import Path

# Bootstrap-Env
import sys

from bootstrap_env import boot_bootstrap_env
from bootstrap_env.boot_bootstrap_env import VerboseSubprocess
from bootstrap_env_tests.base import BootstrapEnvTestCase
from bootstrap_env_tests.utils import IsolatedFilesystem, requirements


class TestBootstrapEnvBoot(BootstrapEnvTestCase):
    """
    Tests for bootstrap_env/boot_bootstrap_env.py

    Note: Travis-CI used boot_bootstrap_env.py to bootstrap into "normal" and "develop" mode!
        No need to test is here again ;)
        Unfortunately, however, the coverage for bootstrapping are missing.
    """
    @unittest.skipIf(requirements.normal_mode, "Executeable is not set by PyPi installation")
    def test_executable(self):
        file_path = Path(boot_bootstrap_env.__file__).resolve()
        self.assertTrue(file_path.is_file())
        self.assertTrue(
            os.access(str(file_path), os.X_OK),
            "File '%s' not executeable!" % file_path
        )

    def test_subprocess_accept_pathlib_args(self):
        self.assertRaises(AssertionError, VerboseSubprocess, Path("/foo/bar"))

    def test_subprocess_accept_pathlib_kwargs(self):
        self.assertRaises(AssertionError, VerboseSubprocess, foo=Path("/foo/bar"))

    def boot_bootstrap_env_run(self, *args):
        boot_file = Path(self.base_path, "boot_bootstrap_env.py")
        args = (str(boot_file), ) + args

        if sys.platform == 'win32':
            args = ("python",) + args

        return VerboseSubprocess(*args).verbose_output(check=False)

    def test_help(self):
        output = self.boot_bootstrap_env_run("help")
        print(output)

        self.assertIn("boot_bootstrap_env.py shell", output)
        self.assertIn("Available commands (type help <topic>):", output)

        self.assertIn("boot", output)
        self.assertIn('Bootstrap bootstrap_env virtualenv in "normal" mode.', output)

        self.assertIn("boot_developer", output)
        self.assertIn('Bootstrap bootstrap_env virtualenv in "developer" mode.', output)

        # If DocString is missing in do_<name>():
        self.assertNotIn("Undocumented", output)

    def test_boot_into_existing_path(self):
        with IsolatedFilesystem(prefix="test_boot_into_existing_path"):
            temp_path = Path().cwd() # isolated_filesystem does made a chdir to /tmp/...

            with self.assertRaises(subprocess.CalledProcessError) as cm:
                output = self.boot_bootstrap_env_run("boot", str(temp_path))
                print(output)

            caller_process_error = cm.exception
            output = caller_process_error.output
            print(output)

            self.assertIn("ERROR: Path '%s' already exists!" % temp_path, output)

    def test_boot_with_activated_venv(self):
        with IsolatedFilesystem(prefix="test_boot_with_activated_venv"):
            temp_path = Path().cwd() # isolated_filesystem does made a chdir to /tmp/...
            destination = Path(temp_path, "test") # a not existing path

            try:
                output = self.boot_bootstrap_env_run("boot", str(destination))
                print(output)
            except subprocess.CalledProcessError as err:
                print(err)
                output = err.output
                print(output)
                self.assertIn("Don't call me in a activated virtualenv!", output)
                self.assertIn("ERROR: Creating virtualenv!", output)
            else:
                self.fail("Doesn't abort!")
