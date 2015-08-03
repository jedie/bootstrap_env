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
from bootstrap_env.tests.utils.utils import get_new_exe_messages
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
            Use %(pip_temp)r
            get-pip.py SHA256: '%(sha)s', ok.

            '%(boot)s' written.
        """ % {
            "boot": self.boot_example_py_path,

            "extend_parser": cut_path(self.extend_parser_py_path),
            "adjust_options": cut_path(self.adjust_options_py_path),
            "after_install": cut_path(self.after_install_py_path),
            "bootstrap_install_pip": cut_path(self.bootstrap_install_pip_py_path),
            "pip_temp": os.path.join(tempfile.gettempdir(), "get-pip.py"),

            "sha": GET_PIP_SHA256,
        }
        #self.assertEqual_dedent(stdout, expected_out) # will fail on travis, e.g.: https://travis-ci.org/jedie/bootstrap_env/jobs/65449993

        self.assert_content(
            content=stdout,
            must_contain=(
                "example", "extend_parser.py", "adjust_options.py", "after_install.py",
                "utils","bootstrap_install_pip.py",
                "Use %r" % get_pip_tempfile(),
                "get-pip.py SHA256: '%s', ok." % GET_PIP_SHA256,
                "boot_example_env.py' written"
            ),
            must_not_contain=(
                "Error", "Traceback"
            )
        )
        self.assertTrue(stdout.count("Read code from:"), 4)
        self.assertEqual(retcode, 0)

        self.assert_is_file(self.boot_example_py_path)

        ###############################################################################
        # Test 'boot_example.py --help' output

        retcode, stdout = self.subprocess(
            popen_args=[sys.executable, self.boot_example_py_path, "--help"],
            verbose=False
        )
        self.assert_content(
            content=stdout,
            must_contain=(
                "The additional example extend_parser() code is called.",
                "Usage: boot_example_env.py [OPTIONS] DEST_DIR",
            ),
            must_not_contain=(
                "Error", "Traceback"
            )
        )
        self.assertEqual(retcode, 0)

        ###############################################################################
        # Test 'boot_example.py' by creating the virtualenv

        with TempDir(prefix="bootstrap_env_example_test_") as tempfolder:
            retcode, stdout = self.subprocess(
                popen_args=[sys.executable, self.boot_example_py_path, tempfolder],
                verbose=False
            )
            must_contain=(
                "The additional example extend_parser() code is called.",
                "The additional example adjust_options() code is called.",
            )

            must_contain += tuple(
                get_new_exe_messages(base_path=tempfolder)
            )

            must_contain += (
                "install pip from self contained 'get_pip.py'",
                "Using cached pip",
                "Using cached setuptools",
                "Using cached wheel",
                "Successfully installed",
                "The additional example after_install() code is called.",
            )

            self.assert_content(
                content=stdout,
                must_contain=must_contain,
                must_not_contain=(
                    "Error", "Traceback",
                )
            )
            self.assertEqual(retcode, 0)

            # TODO: Test the created environment!

        # cleaned?
        self.assert_not_is_dir(tempfolder)