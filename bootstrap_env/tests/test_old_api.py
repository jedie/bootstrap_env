# coding: utf-8

"""
    unittest
    ~~~~~~~~

    :copyleft: 2015 by bootstrap-env team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

import io
import os
import sys
import tempfile

PY3 = sys.version_info[0] == 3

from bootstrap_env.tests.utils.base_unittest import BaseExampleTestCase, StdoutStderrBuffer


class TestOldApi(BaseExampleTestCase):
    maxDiff=2000

    def test_old_api(self):
        """
        Test if the old API works and if we get the 'FutureWarning'
        """
        with tempfile.NamedTemporaryFile(prefix="bootstrap_env_test_") as temp:
            out_filename = temp.name

            with StdoutStderrBuffer() as buffer:
                from bootstrap_env import create_bootstrap
                create_bootstrap.generate_bootstrap(
                    out_filename=out_filename,
                    add_extend_parser=self.extend_parser_py_path,
                    add_adjust_options=self.adjust_options_py_path,
                    add_after_install=self.after_install_py_path,
                    cut_mark="# --- CUT here ---",
                )

            output = buffer.get_output()

            self.assertIn("FutureWarning: You use the old bootstrap_env API!", output)

            self.assertIn("Generate bootstrap file: '%s'..." % out_filename, output)
            self.assertIn("'%s' written" % out_filename, output)
            self.assertNotIn("Error", output)
            self.assertNotIn("Traceback", output)
