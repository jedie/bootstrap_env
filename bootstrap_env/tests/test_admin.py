
"""
    :created: 11.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""
import contextlib
import io
import os
import unittest
from pathlib import Path

# Bootstrap-Env
from bootstrap_env import bootstrap_env_admin
from bootstrap_env.boot_bootstrap_env import VerboseSubprocess
from bootstrap_env.tests.base import BootstrapEnvTestCase
from bootstrap_env.tests.utils import path_helper


class TestBootstrapEnvAdmin(BootstrapEnvTestCase):
    """
    Tests for bootstrap_env/bootstrap_env_admin.py
    """
    maxDiff=None

    @unittest.skipIf(path_helper.normal_mode, "Executeable is not set by PyPi installation")
    def test_executable(self):
        file_path = Path(bootstrap_env_admin.__file__).resolve()
        self.assertTrue(file_path.is_file())
        self.assertTrue(
            os.access(str(file_path), os.X_OK),
            "File '%s' not executeable!" % file_path
        )

    def bootstrap_env_admin_run(self, *args):
        return self._call(*args, filename="bootstrap_env_admin.py")

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

    @unittest.skipIf(path_helper.normal_mode, "Only available in 'developer' mode.")
    def test_change_editable_address(self):
        """
        All test runs on Travis-CI install PyLucid as editable!
        See .travis.yml
        """
        self.assertFalse(path_helper.normal_mode)

        bootstrap_env_src_path = path_helper.base.parent
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

    @unittest.skipIf(path_helper.normal_mode, "Only available in 'developer' mode.")
    def test_update_own_boot_file_nothing_changed(self):
        """
        own bootstrap file should be always up-to-date with the source file from.

            bootstrap_env/boot_bootstrap_env.py
        is generated from:
            bootstrap_env/boot_source/{{cookiecutter.project_name}}/boot_{{cookiecutter.project_name}}.py
        """
        bootstrap_file = Path(self.base_path, "boot_bootstrap_env.py")
        self.assertTrue(bootstrap_file.is_file())

        with bootstrap_file.open("r", encoding="UTF-8") as f:
            old_content = f.read()

        output = self.bootstrap_env_admin_run("update_own_boot_file")
        print(output)

        self.assertIn("Update 'bootstrap_env/boot_bootstrap_env.py' via cookiecutter", output)
        self.assertIn("bootstrap file created", output)

        with bootstrap_file.open("r", encoding="UTF-8") as f:
            content = f.read()

        self.assert_equal_unified_diff(old_content, content)

    @unittest.skipIf(path_helper.normal_mode, "Only available in 'developer' mode.")
    def test_update_own_boot_file_overwrite(self):
        """
        1. Change own, generates bootfile
        2. call "update_own_boot_file"
        3. check if new, generated is ok
        """
        bootstrap_file = Path(self.base_path, "boot_bootstrap_env.py")
        self.assertTrue(bootstrap_file.is_file())

        with bootstrap_file.open("r", encoding="UTF-8") as f:
            old_content = f.read()

        try:
            # replace current bootstrap file:
            with bootstrap_file.open("a", encoding="UTF-8") as f:
                f.write("\n# new line from: test_update_own_boot_file_overwrite()\n")

            output = self.bootstrap_env_admin_run("update_own_boot_file")

            with bootstrap_file.open("r", encoding="UTF-8") as f:
                content = f.read()
        finally:
            # revert any changes with the origin code:
            with bootstrap_file.open("w", encoding="UTF-8") as f:
                f.write(old_content)

        print(output)
        self.assertIn("Update 'bootstrap_env/boot_bootstrap_env.py' via cookiecutter", output)
        self.assertIn("bootstrap file created", output)

        self.assert_equal_unified_diff(old_content, content)

    @unittest.skipIf(path_helper.normal_mode, "Only available in 'developer' mode.")
    def test_newer_source_boot_file(self):
        """
        1. Change the source bootfile
        2. call "update_own_boot_file"
        3. check if new, generated is up-to-date
        """
        bootstrap_file = Path(self.base_path, "boot_bootstrap_env.py")
        with bootstrap_file.open("r", encoding="UTF-8") as f:
            old_content = f.read()

        self.assertNotIn("test_newer_source_boot_file", old_content)

        source_bootstrap_file = Path(
            self.base_path, "boot_source", "{{cookiecutter.project_name}}", "{{cookiecutter.bootstrap_filename}}.py"
        )
        with source_bootstrap_file.open("r", encoding="UTF-8") as f:
            origin_source_content = f.read()

        try:
            with source_bootstrap_file.open("a", encoding="UTF-8") as f:
                f.write("\n# new line from: test_newer_source_boot_file()\n")

            output = self.bootstrap_env_admin_run("update_own_boot_file")

            with bootstrap_file.open("r", encoding="UTF-8") as f:
                new_content = f.read()
        finally:
            # revert any changes with the origin code:
            with source_bootstrap_file.open("w", encoding="UTF-8") as f:
                f.write(origin_source_content)

            with bootstrap_file.open("w", encoding="UTF-8") as f:
                f.write(old_content)

        print(output)

        self.assertIn("Update 'bootstrap_env/boot_bootstrap_env.py' via cookiecutter", output)
        self.assertIn("bootstrap file created", output)

        result = self.unified_diff(
            old_content, new_content,
            fromfile="OLD: boot_bootstrap_env.py",
            tofile="NEW: boot_bootstrap_env.py",
        )
        # print("".join(result))

        result = [line for line in result if "@@" not in line] # evalate genrator and skip all line numbers
        result = "".join(result)
        print(repr(result))

        self.assertEqual(
            result,
            (
                "--- OLD: boot_bootstrap_env.py\n"
                "+++ NEW: boot_bootstrap_env.py\n"
                " if __name__ == '__main__':\n"
                "     # Start the shell\n"
                "     BootBootstrapEnvShell().cmdloop()\n"
                "+\n"
                "+# new line from: test_newer_source_boot_file()\n"
            )
        )

    def test_path_helper_print_path(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            path_helper.print_path()

        output = f.getvalue()
        print(output)

        self.assertIn("egg name .......: 'bootstrap_env'", output)

        if path_helper.normal_mode:
            self.assertIn("/site-packages/bootstrap_env/requirements/normal_installation.txt", output)
        else:
            # dev.mode
            self.assertIn("src/bootstrap-env/bootstrap_env/requirements/developer_installation.txt", output)

    def test_path_helper_assert_all_path(self):
        path_helper.assert_all_path()

    def test_install_test_requirements(self):
        output = self.bootstrap_env_admin_run("install_test_requirements")
        print(output)

        self.assertIn("Requirement already satisfied:", output)
        self.assertIn("/requirements/test_requirements.txt", output)
        self.assertIn("Exit code 0 from ", output)

        self.assertNotIn("Error", output)

    def test_update_env(self):
        output = self.bootstrap_env_admin_run("update_env")
        print(output)

        if path_helper.normal_mode:
            self.assertIn("/site-packages/bootstrap_env/requirements/normal_installation.txt", output)
        else:
            # dev.mode
            self.assertIn("src/bootstrap-env/bootstrap_env/requirements/developer_installation.txt", output)

        self.assertIn("Successfully installed bootstrap-env", output)
        self.assertIn("Please restart bootstrap_env_admin.py", output)

        self.assertNotIn("Error", output)
