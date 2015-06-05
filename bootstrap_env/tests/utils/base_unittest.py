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
import shutil
import sys
import tempfile
import textwrap
import unittest
from contextlib import contextmanager

PY3 = sys.version_info[0] == 3

import bootstrap_env
import bootstrap_env.example
from bootstrap_env.utils import bootstrap_install_pip
from bootstrap_env.tests.utils.unittest_subprocess import SubprocessMixin
from bootstrap_env.utils.get_pip import get_pip, get_pip_tempfile
from bootstrap_env.utils.sourcecode_utils import abs_py_path


class StdoutStderrBuffer():
    """
    redirect stderr and stdout for Py2 and Py3

    contextlib.redirect_stdout is new in Python 3.4!
    and we redirect stderr, too.
    """
    def __init__(self):
        sys.stdout.flush()
        sys.stderr.flush()
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        if PY3:
            self.buffer = io.StringIO()
        else:
            self.buffer = io.BytesIO()

        sys.stdout = sys.stderr = self.buffer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.old_stdout.flush()
        self.old_stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    def get_output(self):
        self.old_stdout.flush()
        self.old_stderr.flush()
        output = self.buffer.getvalue()
        if not PY3:
            output = output.decode("utf-8")
        return output



class TempDir():
    def __init__(self, prefix=""):
        self.tempfolder = tempfile.mkdtemp(prefix=prefix)

    def __enter__(self):
        return self.tempfolder

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.tempfolder)



def _get_pip_for_unittests():
    from_request = None
    from_temp = None

    get_pip_temp = get_pip_tempfile()

    with StdoutStderrBuffer() as buffer:
        get_pip_content = get_pip()
    output = buffer.get_output()

    if "Request" in output:
        from_request = output
    else:
        from_temp = output

    return get_pip_temp, from_request, from_temp


class BaseUnittestCase(unittest.TestCase, SubprocessMixin):
    BASE_PATH=os.path.abspath(
        os.path.join(
            os.path.dirname(bootstrap_env.__file__), ".."
        )
    )
    PIP_FROM_TEMP=None
    PIP_FROM_REQUEST=None

    IS_PYPY = hasattr(sys, 'pypy_version_info')

    @classmethod
    def setUpClass(cls):
        """
        Assume that pip is used always from temp
        so that subprocess output is always the same
        """
        get_pip_temp, from_request, from_temp = _get_pip_for_unittests()

        cls.get_pip_temp = get_pip_temp
        cls.PIP_FROM_REQUEST = from_request
        cls.PIP_FROM_TEMP = from_temp

        cls.bootstrap_install_pip_py_path = abs_py_path(bootstrap_install_pip)

    def _dedent(self, txt):
        # Remove any common leading whitespace from every line
        txt = textwrap.dedent(txt)

        # strip whitespace at the end of every line
        txt = "\n".join([line.rstrip() for line in txt.splitlines()])
        txt = txt.strip()
        return txt

    def assertEqual_dedent(self, first, second, msg=None):
        first = self._dedent(first)
        second = self._dedent(second)
        try:
            self.assertEqual(first, second, msg)
        except AssertionError as err:
            # Py2 has a bad error message
            msg = (
                "%s\n"
                " ------------- [first] -------------\n"
                "%s\n"
                " ------------- [second] ------------\n"
                "%s\n"
                " -----------------------------------\n"
            ) % (err, first, second)
            raise AssertionError(msg)

    def assert_is_dir(self, path):
        self.assertTrue(os.path.isdir(path), "Directory %r doesn't exists!" % path)

    def assert_not_is_dir(self, path):
        self.assertFalse(os.path.isdir(path), "Directory %r exists, but should not exists!" % path)

    def assert_is_file(self, path):
        self.assertTrue(os.path.isfile(path), "File %r doesn't exists!" % path)

    def assert_not_is_File(self, path):
        self.assertFalse(os.path.isfile(path), "File %r exists, but should not exists!" % path)

    def set_get_pip_output(self):
        get_pip_temp, from_request, from_temp = _get_pip_for_unittests()
        if from_request is not None:
            self.PIP_FROM_REQUEST = from_request
        if from_temp is not None:
            self.PIP_FROM_TEMP = from_temp


class BaseExampleTestCase(BaseUnittestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseExampleTestCase, cls).setUpClass()
        cls.example_path=os.path.dirname(abs_py_path(bootstrap_env.example))
        # cls.assert_is_dir(cls, cls.example_path) # doesn't work in Py2 :(
        assert os.path.isdir(cls.example_path), "Directory %r doesn't exists!" % cls.example_path

        def join_existing_file(path, filename):
            py_path=os.path.join(path, filename)
            # cls.assert_is_file(cls, py_path) # doesn't work in Py2 :(
            assert os.path.isfile(py_path), "File %r doesn't exists!" % py_path
            return py_path

        cls.extend_parser_py_path=join_existing_file(cls.example_path, "extend_parser.py")
        cls.adjust_options_py_path=join_existing_file(cls.example_path, "adjust_options.py")
        cls.after_install_py_path=join_existing_file(cls.example_path, "after_install.py")

        cls.create_example_py_path=join_existing_file(cls.example_path, "create_example.py")

        # the created boot file: Doesn't exists
        cls.boot_example_py_path = os.path.join(cls.BASE_PATH, "boot_example_env.py")
