
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

import bootstrap_env
from bootstrap_env import bootstrap_env_admin
from bootstrap_env.boot_bootstrap_env import VerboseSubprocess
from bootstrap_env_tests.base import BootstrapEnvTestCase
from bootstrap_env_tests.utils import requirements


class TestBootstrapEnvAdmin(BootstrapEnvTestCase):
    """
    Tests for bootstrap_env/bootstrap_env_admin.py
    """
    @unittest.skipIf(requirements.normal_mode, "Executeable is not set by PyPi installation")
    def test_executable(self):
        file_path = Path(bootstrap_env_admin.__file__).resolve()
        self.assertTrue(file_path.is_file())
        self.assertTrue(
            os.access(str(file_path), os.X_OK),
            "File '%s' not executeable!" % file_path
        )

    def bootstrap_env_admin_run(self, *args):
        admin_file = Path(self.base_path, "bootstrap_env_admin.py")
        args = (str(admin_file), ) + args

        if sys.platform == 'win32':
            args = ("python",) + args

        try:
            return VerboseSubprocess(*args).verbose_output(check=False)
        except subprocess.CalledProcessError as err:
            self.fail(
                (
                    "Subprocess error: %s"
                    "\noutput:"
                    "\n%s"
                ) % (err, err.output)
            )

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

    @unittest.skipIf(requirements.normal_mode, "Only available in 'developer' mode.")
    def test_change_editable_address(self):
        """
        All test runs on Travis-CI install PyLucid as editable!
        See .travis.yml
        """
        self.assertFalse(requirements.normal_mode)

        bootstrap_env_src_path = Path(requirements.src_path, "bootstrap-env")
        print("bootstrap_env_src_path: %r" % bootstrap_env_src_path)

        self.assertTrue(bootstrap_env_src_path.is_dir(), "Directory not exists: %s" % bootstrap_env_src_path)
        self.assertTrue(str(bootstrap_env_src_path).endswith("/src/bootstrap-env"))

        git_path = Path(bootstrap_env_src_path, ".git")
        print("git_path: %r" % git_path)

        VerboseSubprocess("ls", "-la", str(bootstrap_env_src_path)).verbose_call(check=False)

        self.assertTrue(git_path.is_dir(), "Directory not exists: %s" % git_path)

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

    @unittest.skipIf(requirements.normal_mode, "Only available in 'developer' mode.")
    def test_update_own_boot_file_nothing_changed(self):
        """
        own bootstrap file should be always up-to-date with the source file from.

            bootstrap_env/boot_bootstrap_env.py
        is generated from:
            bootstrap_env/boot_source/{{cookiecutter.project_name}}/boot_{{cookiecutter.project_name}}.py
        """
        bootstrap_file = Path(self.base_path, "boot_bootstrap_env.py")
        self.assertTrue(bootstrap_file.is_file())

        with bootstrap_file.open("r") as f:
            old_content = f.read()

        output = self.bootstrap_env_admin_run("update_own_boot_file")
        print(output)

        self.assertIn("Update 'bootstrap_env/boot_bootstrap_env.py' via cookiecutter", output)
        self.assertIn("bootstrap file created", output)

        with bootstrap_file.open("r") as f:
            content = f.read()

        self.assertEqual(old_content, content)

    @unittest.skipIf(requirements.normal_mode, "Only available in 'developer' mode.")
    def test_update_own_boot_file_overwrite(self):
        bootstrap_file = Path(self.base_path, "boot_bootstrap_env.py")
        self.assertTrue(bootstrap_file.is_file())

        with bootstrap_file.open("r") as f:
            old_content = f.read()

        try:
            # replace current bootstrap file:
            with bootstrap_file.open("a") as f:
                f.write("# new line from: test_update_own_boot_file_overwrite()")

            output = self.bootstrap_env_admin_run("update_own_boot_file")
            print(output)

            self.assertIn("Update 'bootstrap_env/boot_bootstrap_env.py' via cookiecutter", output)
            self.assertIn("bootstrap file created", output)

            with bootstrap_file.open("r") as f:
                content = f.read()

            self.assertEqual(old_content, content)
        finally:
            # revert any changes with the origin code:
            with bootstrap_file.open("w") as f:
                f.write(old_content)
