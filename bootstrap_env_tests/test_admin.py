
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
from bootstrap_env import bootstrap_env_admin
from bootstrap_env.boot_bootstrap_env import VerboseSubprocess
from bootstrap_env.bootstrap_env_admin import Requirements


class TestPyLucidAdmin(unittest.TestCase):
    """
    Tests for bootstrap_env/bootstrap_env_admin.py
    """
    def test_executable(self):
        file_path = Path(bootstrap_env_admin.__file__).resolve()
        self.assertTrue(file_path.is_file())
        self.assertTrue(
            os.access(str(file_path), os.X_OK),
            "File '%s' not executeable!" % file_path
        )

    def bootstrap_env_admin_run(self, *args):
        args = ("bootstrap_env_admin.py", ) + args
        try:
            return VerboseSubprocess(*args).verbose_output(check=False)
        except subprocess.CalledProcessError as err:
            self.fail("Subprocess error: %s" % err)

    def test_help(self):
        output = self.bootstrap_env_admin_run("help")
        print(output)

        self.assertIn("bootstrap_env_admin.py shell", output)

        self.assertIn("Available commands (type help <topic>):", output)

        self.assertIn("update_env", output)
        self.assertIn("Update all packages in virtualenv.", output)

        # If DocString is missing in do_<name>():
        self.assertNotIn("Undocumented", output)

    def test_unknown_command(self):
        output = self.bootstrap_env_admin_run("foo bar is unknown ;)")
        print(output)

        self.assertIn("bootstrap_env_admin.py shell", output)
        self.assertIn("*** Unknown command: 'foo bar is unknown ;)' ***", output)

    @unittest.skipIf(Requirements().normal_mode, "Only available in 'developer' mode.")
    def test_change_editable_address(self):
        """
        All test runs on Travis-CI install PyLucid as editable!
        See .travis.yml
        """
        req = Requirements()

        self.assertFalse(Requirements().normal_mode)

        bootstrap_env_src_path = Path(req.src_path, "bootstrap-env")
        print("bootstrap_env_src_path: %r" % bootstrap_env_src_path)

        self.assertTrue(bootstrap_env_src_path.is_dir())
        self.assertTrue(str(bootstrap_env_src_path).endswith("/src/bootstrap-env"))

        git_path = Path(bootstrap_env_src_path, ".git")
        print("git_path: %r" % git_path)

        self.assertTrue(git_path.is_dir())

        # Needed while developing with github write access url ;)
        output = VerboseSubprocess(
            "git", "remote", "set-url", "origin", "https://github.com/jedie/bootstrap_env.git",
            cwd=str(bootstrap_env_src_path)
        ).verbose_output(check=True)
        # print(output)

        # Check if change was ok:
        output = VerboseSubprocess(
            "git", "remote", "-v",
            cwd=str(bootstrap_env_src_path)
        ).verbose_output(check=True)
        # print(output)
        self.assertIn("https://github.com/jedie/bootstrap_env.git", output)
        self.assertNotIn("git@github.com", output)

        output = self.bootstrap_env_admin_run("change_editable_address")
        print(output)

        self.assertIn("git@github.com:jedie/bootstrap_env.git", output)
