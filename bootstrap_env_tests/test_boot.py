
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
from bootstrap_env import boot_bootstrap_env
from bootstrap_env.boot_bootstrap_env import VerboseSubprocess
from bootstrap_env_tests.utils import IsolatedFilesystem


class TestPyLucidBoot(unittest.TestCase):
    """
    Tests for bootstrap_env/boot_bootstrap_env.py

    Note: Travis-CI used boot_bootstrap_env.py to bootstrap into "normal" and "develop" mode!
        No need to test is here again ;)
        Unfortunately, however, the coverage for bootstrapping are missing.
    """
    def test_executable(self):
        file_path = Path(boot_bootstrap_env.__file__).resolve()
        self.assertTrue(file_path.is_file())
        self.assertTrue(
            os.access(str(file_path), os.X_OK),
            "File '%s' not executeable!" % file_path
        )

    def pylucid_admin_run(self, *args):
        args = ("boot_bootstrap_env.py", ) + args
        try:
            return VerboseSubprocess(*args).verbose_output(check=False)
        except subprocess.CalledProcessError as err:
            print(err.output)
            self.fail("Subprocess error: %s" % err)

    def test_help(self):
        output = self.pylucid_admin_run("help")
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
                VerboseSubprocess("boot_bootstrap_env.py", "boot", str(temp_path)).verbose_output(check=False)

            caller_process_error = cm.exception
            output = caller_process_error.output
            print(output)

            self.assertIn("ERROR: Path '%s' already exists!" % temp_path, output)
