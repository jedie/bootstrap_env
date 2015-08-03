# coding: utf-8

"""
    unittest
    ~~~~~~~~

    :copyleft: 2015 by bootstrap-env team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

import os
import shutil
import sys
import tempfile

from bootstrap_env.tests.utils.base_unittest import BaseExampleTestCase, TempDir, StdoutStderrBuffer
from bootstrap_env.tests.utils.utils import get_new_exe_messages
from bootstrap_env.utils import bootstrap_install_pip
from bootstrap_env.utils.get_pip import GET_PIP_SHA256, get_pip_tempfile
from bootstrap_env.example import extend_parser, adjust_options, after_install

from bootstrap_env.boot_bootstrap_env.create_boot import generate as generate_boot_file
from bootstrap_env.boot_bootstrap_env.create_boot import BOOT_FILEPATH
from bootstrap_env.boot import main as boot_main
from bootstrap_env.boot import __version__ as used_virtualenv_version

IS_PYPY = hasattr(sys, 'pypy_version_info')

# @unittest.skip
from bootstrap_env.utils.sourcecode_utils import cut_path, abs_py_path

class TestGenerateBoot(BaseExampleTestCase):
    """
    test generation of boot.py
    """
    def setUp(self):
        self.boot_filepath_bak = BOOT_FILEPATH + ".OLD"
        os.rename(BOOT_FILEPATH, self.boot_filepath_bak)

    def tearDown(self):
        try:
            os.remove(BOOT_FILEPATH)
        except OSError:
            pass

        os.rename(self.boot_filepath_bak, BOOT_FILEPATH)

    def test_generate(self):
        # Check if the "old" boot.py was renamed
        self.assert_is_file(self.boot_filepath_bak)
        self.assert_not_is_File(BOOT_FILEPATH)

        with StdoutStderrBuffer() as buffer:
            generate_boot_file()

        output = buffer.get_output()
        # print(output)

        self.assert_content(
            content=output,
            must_contain=(
                "requirements from 'normal_installation.txt':",
                "requirements from 'git_readonly_installation.txt':",
                "requirements from 'developer_installation.txt':",

                "boot_bootstrap_env","sources",
                "prefix_code.py", "extend_parser.py", "adjust_options.py", "after_install.py",
                "bootstrap_env","utils","bootstrap_install_pip.py",

                "Use %r" % get_pip_tempfile(),
                "get-pip.py SHA256: '%s', ok." % GET_PIP_SHA256,
                "%r written." % BOOT_FILEPATH,
            ),
            must_not_contain=(
                "Error", "Traceback"
            )
        )
        self.assertTrue(output.count("Read code from:"), 5)

        self.assert_is_file(BOOT_FILEPATH)

        # Test the generated boot.py

        retcode, stdout = self.subprocess(
            popen_args=[sys.executable, BOOT_FILEPATH, "--help"],
            verbose=False
        )
        self.assert_content(
            content=stdout,
            must_contain=(
                "Usage: boot.py [OPTIONS] DEST_DIR",
                "--install_type=INSTALL_TYPE",
                "Install type: pypi, git_readonly, dev (See README!)",
            ),
            must_not_contain=(
                "Error", "Traceback"
            )
        )
        self.assertEqual(retcode, 0)



class TestBoot(BaseExampleTestCase):
    """
    Test with existing boot.py
    """
    maxDiff=4000

    def setUp(self):
        self.origin_argv = sys.argv[:] # .copy() not exist in Py2 !
        sys.argv = [BOOT_FILEPATH]

    def tearDown(self):
        sys.argv = self.origin_argv

    def test_boot_help(self):
        return_code = None
        with StdoutStderrBuffer() as buffer:
            sys.argv.append("--help")
            try:
                boot_main()
            except SystemExit as err:
                return_code = err.code

        output = buffer.get_output()
        self.assertIn("Usage: boot.py [OPTIONS] DEST_DIR", output)
        self.assertIn("--install_type=INSTALL_TYPE", output)
        self.assertIn("Install type: pypi, git_readonly, dev (See README!)", output)
        self.assertEqual(return_code, 0)

    def test_boot_version(self):
        return_code = None
        with StdoutStderrBuffer() as buffer:
            sys.argv.append("--version")
            try:
                boot_main()
            except SystemExit as err:
                return_code = err.code

        output = buffer.get_output()
        self.assertEqual("%s\n" % used_virtualenv_version, output)
        self.assertEqual(return_code, 0)

    def test_boot_git_readonly(self):
        # python bootstrap_env/boot.py ${BUILD_DIR} --install_type git_readonly

        return_code = None
        with TempDir(prefix="bootstrap_test_boot_git_readonly_") as tempfolder:
            sys.argv += ["--install_type=git_readonly", tempfolder]

            with StdoutStderrBuffer() as buffer:
                try:
                    boot_main()
                except SystemExit as err:
                    return_code = err.code

            output = buffer.get_output()
            # print("-"*79)
            # print(output)
            # print("="*79)
            must_contain = (
                "Install type: 'git_readonly'",
            )

            must_contain += tuple(
                get_new_exe_messages(base_path=tempfolder)
            )
            self.assert_content(
                content=output,
                must_contain=must_contain,
                must_not_contain=(
                    "Error", "Traceback",
                )
            )
            self.assertEqual(return_code, None) # no sys.exit()

            # TODO: Test the created environment!

            with open(os.path.join(tempfolder, "install.log"), "r") as f:
                log_content = f.read()
                self.assert_content(
                    content=log_content,
                    must_contain=(
                        "Cloning https://github.com/jedie/bootstrap_env.git",
                        "Successfully installed bootstrap-env",
                    ),
                    must_not_contain=(
                        "Error", "Traceback",
                    )
                )

        # cleaned?
        self.assert_not_is_dir(tempfolder)