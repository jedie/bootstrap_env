
"""
    :created: 03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""
import difflib
import subprocess
import sys
import unittest
from pathlib import Path

# Bootstrap-Env
import bootstrap_env
from bootstrap_env.boot_bootstrap_env import VerboseSubprocess


class BootstrapEnvTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_path = Path(bootstrap_env.__file__).resolve().parent

    def test_setup(self):
        self.assertTrue(self.base_path.is_dir())

    def _call(self, *args, filename=None):
        assert filename is not None

        file_path = Path(self.base_path, filename)
        assert file_path.is_file()

        args = (sys.executable or "python3", str(file_path), ) + args
        try:
            return VerboseSubprocess(*args).verbose_output(check=False)
        except subprocess.CalledProcessError as err:
            msg = (
                "Subprocess error: %s"
                "\noutput:"
                "\n%s"
            ) % (err, err.output)
            print(msg)
            raise

    def unified_diff(self, first, second, fromfile="first", tofile="second"):
        if isinstance(first, str):
            first = first.splitlines(keepends=True)

        if isinstance(second, str):
            second = second.splitlines(keepends=True)

        result = difflib.unified_diff(first, second, fromfile=fromfile, tofile=tofile)
        return result

    def assert_equal_unified_diff(self, first, second, fromfile="first", tofile="second"):
        """
        Same as self.assertEqual() but output a unified diff.
        """
        if first == second:
            return

        result = self.unified_diff(first, second, fromfile=fromfile, tofile=tofile)
        msg="Content is not equal, unified diff:\n%s" % "".join(result)
        self.fail(msg)
