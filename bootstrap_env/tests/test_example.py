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

from bootstrap_env.tests.utils.base_unittest import BaseExampleTestCase, TempDir
from bootstrap_env.utils import bootstrap_install_pip
from bootstrap_env.utils.get_pip import GET_PIP_SHA256, get_pip_tempfile
from bootstrap_env.example import extend_parser, adjust_options, after_install


# @unittest.skip
from bootstrap_env.utils.sourcecode_utils import cut_path, abs_py_path


class TestExample(BaseExampleTestCase):
    maxDiff=2000

    def tearDown(self):
        try:
            os.remove(self.boot_example_py_path)
        except OSError: # FileNotFoundError doesn't exist on Py2
            pass

    def test_example(self):
        self.assertFalse(
            os.path.isfile(self.boot_example_py_path),
            "Error: %s exists, but should not exist!" % self.boot_example_py_path
        )
        self.assert_is_file(self.create_example_py_path)

        retcode, stdout = self.subprocess(
            popen_args=[sys.executable, self.create_example_py_path],
            verbose=False
        )
        expected_out = """
            Generate bootstrap file: '%(boot)s'...

            Read code from: '%(extend_parser)s'...
            Read code from: '%(adjust_options)s'...
            Read code from: '%(after_install)s'...
            Read code from: '%(bootstrap_install_pip)s'...
            Use '/tmp/get-pip.py'
            get-pip.py SHA256: '%(sha)s', ok.

            '%(boot)s' written.
        """ % {
            "boot": self.boot_example_py_path,

            "extend_parser": cut_path(self.extend_parser_py_path),
            "adjust_options": cut_path(self.adjust_options_py_path),
            "after_install": cut_path(self.after_install_py_path),
            "bootstrap_install_pip": cut_path(self.bootstrap_install_pip_py_path),

            "sha": GET_PIP_SHA256,
        }
        #self.assertEqual_dedent(stdout, expected_out) # will fail on travis, e.g.: https://travis-ci.org/jedie/bootstrap_env/jobs/65449993
        self.assertIn("example/extend_parser.py", stdout)
        self.assertIn("example/adjust_options.py", stdout)
        self.assertIn("example/after_install.py", stdout)
        self.assertIn("utils/bootstrap_install_pip.py", stdout)
        self.assertIn("Use '%s'" % get_pip_tempfile(), stdout)
        self.assertIn("get-pip.py SHA256: '%s', ok." % GET_PIP_SHA256, stdout)
        self.assertIn("boot_example_env.py' written", stdout)

        self.assertNotIn("Error", stdout)
        self.assertNotIn("Traceback", stdout)

        self.assertEqual(retcode, 0)

        self.assert_is_file(self.boot_example_py_path)

        ###############################################################################
        # Test 'boot_example.py --help' output

        retcode, stdout = self.subprocess(
            popen_args=[sys.executable, self.boot_example_py_path, "--help"],
            verbose=False
        )
        self.assertIn("The additional example extend_parser() code is called.", stdout)
        self.assertIn("Usage: boot_example_env.py [OPTIONS] DEST_DIR", stdout)
        self.assertEqual(retcode, 0)

        ###############################################################################
        # Test 'boot_example.py' by creating the virtualenv

        with TempDir(prefix="bootstrap_env_example_test_") as tempfolder:
            retcode, stdout = self.subprocess(
                popen_args=[sys.executable, self.boot_example_py_path, tempfolder],
                verbose=False
            )
            self.assertIn("The additional example extend_parser() code is called.", stdout)
            self.assertIn("The additional example adjust_options() code is called.", stdout)

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
                self.assertIn("New pypy executable in %s/bin/python" % tempfolder, stdout)
                self.assertIn("Also creating executable in %s/bin/pypy" % tempfolder, stdout)
            else:
                # *** python2 e.g.:
                # Using real prefix '/opt/python/2.7.9'
                # New python executable in /tmp/bootstrap_env_test_51rIfq/bin/python
                # Install pip...

                # *** python3 e.g.:
                # Using real prefix '/opt/python/3.4.2'
                # New python executable in /tmp/bootstrap_env_test__8cfcmhq/bin/python
                # Install pip...
                self.assertIn("New python executable in %s/bin/python" % tempfolder, stdout)

            self.assertIn("install pip from self contained 'get_pip.py'", stdout)
            self.assertIn("Using cached pip", stdout)
            self.assertIn("Using cached setuptools", stdout)
            self.assertIn("Using cached wheel", stdout)
            self.assertIn("Successfully installed", stdout)

            self.assertIn("The additional example after_install() code is called.", stdout)

            self.assertNotIn("Error", stdout)
            self.assertNotIn("Traceback", stdout)
            self.assertEqual(retcode, 0)

            # TODO: Test the created environment!

        # cleaned?
        self.assert_not_is_dir(tempfolder)