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

from bootstrap_env.utils.get_pip import GET_PIP_SHA256, HASH_GET_PIP_URL, MASTER_GET_PIP_URL
from bootstrap_env.tests.utils.base_unittest import BaseUnittestCase



# @unittest.skip
class TestGetPip(BaseUnittestCase):
    def test_from_temp(self):
        if self.PIP_FROM_TEMP is None:
            # Maybe this test is called at first, then
            # 'get_pip.py' was fresh request from internet
            # So, just request it again and then the temp
            # should be used
            self.set_get_pip_output()

        msg = """
            Use %r
            get-pip.py SHA256: '%s', ok.
        """ % (
            os.path.normpath(self.get_pip_temp), # linux/windows path representation.
            GET_PIP_SHA256
        )
        self.assertEqual_dedent(self.PIP_FROM_TEMP, msg)

    # @unittest.skip
    def test_from_request(self):
        if self.PIP_FROM_REQUEST is None:
            # Maybe the tempfile already exists before tests was running.
            os.remove(self.get_pip_temp)
            self.set_get_pip_output()

        msg = """
            Request: '%s'...
            Request: '%s'...
            Requested content of 'get-pip.py' is up-to-date, ok.
            get-pip.py SHA256: '%s', ok.
        """ % (
            HASH_GET_PIP_URL,
            MASTER_GET_PIP_URL,
            GET_PIP_SHA256
        )
        self.assertEqual_dedent(self.PIP_FROM_REQUEST, msg)