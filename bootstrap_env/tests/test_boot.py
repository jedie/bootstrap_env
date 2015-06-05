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
        self.assertIn("requirements from 'normal_installation.txt':", output)
        self.assertIn("requirements from 'git_readonly_installation.txt':", output)
        self.assertIn("requirements from 'developer_installation.txt':", output)

        self.assertIn("boot_bootstrap_env/sources/prefix_code.py", output)
        self.assertIn("boot_bootstrap_env/sources/extend_parser.py", output)
        self.assertIn("boot_bootstrap_env/sources/adjust_options.py", output)
        self.assertIn("boot_bootstrap_env/sources/after_install.py", output)
        self.assertIn("bootstrap_env/utils/bootstrap_install_pip.py", output)

        self.assertIn("Use '%s'" % get_pip_tempfile(), output)
        self.assertIn("get-pip.py SHA256: '%s', ok." % GET_PIP_SHA256, output)
        self.assertIn("'%s' written." % BOOT_FILEPATH, output)

        self.assert_is_file(BOOT_FILEPATH)

        # Test the generated boot.py

        retcode, stdout = self.subprocess(
            popen_args=[sys.executable, BOOT_FILEPATH, "--help"],
            verbose=False
        )
        self.assertIn("Usage: boot.py [OPTIONS] DEST_DIR", stdout)
        self.assertIn("--install_type=INSTALL_TYPE", stdout)
        self.assertIn("Install type: pypi, git_readonly, dev (See README!)", stdout)
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
            self.assertIn("Install type: 'git_readonly'", output)

            if self.IS_PYPY:
                # *** pypy2 e.g.:
                # Using real prefix '/opt/python/pypy-2.5.0'
                # Path not in prefix '/home/travis/build_pypypy/include' '/opt/python/pypy-2.5.0'
                # New pypy executable in /tmp/bootstrap_env_test_Jwxr5P/bin/python
                # Also creating executable in /tmp/bootstrap_env_test_Jwxr5P/bin/pypy
                # Install pip...

                # *** pypy3 e.g.:
                # Using real prefix '/opt/python/pypy3-2.4.0'
                # Path not in prefix '/home/travis/build_pypypy3/include' '/opt/python/pypy3-2.4.0'
                # New pypy executable in /tmp/bootstrap_env_test_rv1rl3/bin/python
                # Also creating executable in /tmp/bootstrap_env_test_rv1rl3/bin/pypy
                # Install pip...
                self.assertIn("New pypy executable in %s/bin/python" % tempfolder, output)
                self.assertIn("Also creating executable in %s/bin/pypy" % tempfolder, output)
            else:
                # *** python2 e.g.:
                # Using real prefix '/opt/python/2.7.9'
                # New python executable in /tmp/bootstrap_env_test_51rIfq/bin/python
                # Install pip...

                # *** python3 e.g.:
                # Using real prefix '/opt/python/3.4.2'
                # New python executable in /tmp/bootstrap_env_test__8cfcmhq/bin/python
                # Install pip...
                self.assertIn("New python executable in %s/bin/python" % tempfolder, output)

            # FIXME:
            # self.assertIn("Cloning https://github.com/jedie/bootstrap_env.git", output)
            # self.assertIn("Successfully installed bootstrap-env", output)

            self.assertEqual(return_code, None) # no sys.exit()

            # TODO: Test the created environment!

            with open(os.path.join(tempfolder, "install.log"), "r") as f:
                log_content = f.read()
                self.assertIn("Successfully installed bootstrap-env", log_content)

        # cleaned?
        self.assert_not_is_dir(tempfolder)