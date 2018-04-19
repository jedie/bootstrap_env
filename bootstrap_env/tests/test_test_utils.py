
"""
    :created: 23.03.2018 by Jens Diemer, www.jensdiemer.de
    :copyleft: 2018 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU General Public License v3 or later (GPLv3+), see LICENSE for more details.
"""

# Bootstrap-Env
import sys

from bootstrap_env.tests.base import BootstrapEnvTestCase


class TestUtilsTestCase(BootstrapEnvTestCase):
    def test_assert_equal_unified_diff(self):
        first = ["Line %i\n" % no for no in range(100)]
        second = first.copy()

        self.assert_equal_unified_diff(first, second)

        second.insert(50, "Inserted at 50:")

        with self.assertRaises(AssertionError) as cm:
            self.assert_equal_unified_diff(first, second)

        exception = cm.exception
        exception_text = exception.args[0]
        print(repr(exception_text))
        self.assertEqual(exception_text, (
            "Content is not equal, unified diff:\n"
            "--- first\n"
            "+++ second\n"
            "@@ -48,6 +48,7 @@\n"
            " Line 47\n"
            " Line 48\n"
            " Line 49\n"
            "+Inserted at 50: Line 50\n"
            " Line 51\n"
            " Line 52\n"
        ))

    def test_call(self):
        output = self._call("--test", filename=__file__)
        print(output)
        self.assertIn("test_test_utils.py --test", output)


if __name__ == '__main__':
    print("sys.argv:", " ".join(sys.argv))
