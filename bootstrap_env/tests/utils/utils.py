# coding: utf-8

"""
    unittest
    ~~~~~~~~

    :copyleft: 2015 by bootstrap-env team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import print_function, absolute_import

import difflib
import os
import textwrap
import unittest


## error output format:
# =1 -> via repr()
# =2 -> raw
import sys

VERBOSE = 1
#VERBOSE = 2


def make_diff(block1, block2):
    d = difflib.Differ()

    block1 = block1.replace("\\n", "\\n\n").split("\n")
    block2 = block2.replace("\\n", "\\n\n").split("\n")

    diff = d.compare(block1, block2)

    result = ["%2s %s\n" % (line, i) for line, i in enumerate(diff)]
    return "".join(result)


class MarkupTest(unittest.TestCase):
    """
    Special error class: Try to display markup errors in a better way.
    """
    def _format_output(self, txt):
        txt = txt.split("\\n")
        if VERBOSE == 1:
            txt = "".join(['%s\\n\n' % i for i in txt])
        elif VERBOSE == 2:
            txt = "".join(['%s\n' % i for i in txt])
        return txt

    def assertEqual(self, first, second, msg=""):
        if not first == second:
            if VERBOSE >= 2:
                print("first: %r" % first)
                print("second: %r" % second)

            #~ first = first.rstrip("\\n")
            #~ second = second.rstrip("\\n")
            try:
                diff = make_diff(first, second)
            except AttributeError:
                raise self.failureException("%s is not %s" % (repr(first), repr(second)))

            if VERBOSE >= 2:
                print("diff: %r" % diff)

            first = self._format_output(first)
            second = self._format_output(second)

            msg += (
                "\n---[Output:]---\n%s\n"
                "---[not equal to:]---\n%s"
                "\n---[diff:]---\n%s"
            ) % (first, second, diff)
            raise self.failureException(msg)

    def _prepare_text(self, txt):
        """
        prepare the multiline, indentation text.
        """
        txt = txt.splitlines()
        assert txt[0] == "", "First assertion line must be empty! Is: %s" % repr(txt[0])
        txt = txt[1:] # Skip the first line

        # get the indentation level from the first line
        count = False
        for count, char in enumerate(txt[0]):
            if char != " ":
                break

        assert count != False, "second line is empty!"

        # remove indentation from all lines
        txt = [i[count:].rstrip(" ") for i in txt]

        #~ txt = re.sub("\n {2,}", "\n", txt)
        txt = "\n".join(txt)

        # strip *one* newline at the begining...
        if txt.startswith("\n"): txt = txt[1:]
        # and strip *one* newline at the end of the text
        if txt.endswith("\n"): txt = txt[:-1]
        #~ print(repr(txt))
        #~ print("-"*79)

        return txt

    def testSelf(self):
        """
        Test for self._prepare_text()
        """
        out1 = self._prepare_text("""
            one line
            line two""")
        self.assertEqual(out1, "one line\nline two")

        out2 = self._prepare_text("""
            one line
            line two
        """)
        self.assertEqual(out2, "one line\nline two")

        out3 = self._prepare_text("""
            one line

            line two
        """)
        self.assertEqual(out3, "one line\n\nline two")

        out4 = self._prepare_text("""
            one line
                line two

        """)
        self.assertEqual(out4, "one line\n    line two\n")

        # removing whitespace and the end
        self.assertEqual(self._prepare_text("\n  111  \n  222"), "111\n222")

        out5 = self._prepare_text("""
            one line
                line two
            dritte Zeile
        """)
        self.assertEqual(out5, "one line\n    line two\ndritte Zeile")

        self.assertRaises(
            AssertionError, self.assertEqual, "foo", "bar"
        )


def get_new_exe_messages(base_path):
    messages = []

    if sys.platform.startswith('win'):
        python_path = os.path.join(base_path, "Scripts", "python.exe")
    else:
        python_path = os.path.join(base_path, "bin", "python")

    if hasattr(sys, 'pypy_version_info'):
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

        messages.append("New pypy executable in %s" % python_path)

        if sys.platform.startswith('win'):
            pypy_path = os.path.join(base_path, "Scripts", "pypy.exe")
        else:
            pypy_path = os.path.join(base_path, "bin", "pypy")

        messages.append("Also creating executable in %s" % pypy_path)
    else:
        # *** python2 e.g.:
        # Using real prefix '/opt/python/2.7.9'
        # New python executable in /tmp/bootstrap_env_test_51rIfq/bin/python
        # Install pip...

        # *** python3 e.g.:
        # Using real prefix '/opt/python/3.4.2'
        # New python executable in /tmp/bootstrap_env_test__8cfcmhq/bin/python
        # Install pip...
        messages.append("New python executable in %s" % python_path)

    return messages


if __name__ == '__main__':
    import doctest
    print("DocTest:", doctest.testmod())

    unittest.main()
