# coding: utf-8

"""
    :created: 2014 by JensDiemer.de
    :copyleft: 2014-2015 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function
import codecs

import os
import sys

PY2 = sys.version_info[0] == 2

def cut_path(filepath):
    filepath = os.path.normpath(filepath)
    parts = filepath.split(os.sep)
    parts = parts[-5:]
    filepath = "...%s%s" % (os.sep, os.sep.join(parts))
    return filepath


def abs_py_path(obj):
    """
    :return absolute file path from __file__ attribute
    """
    filepath = obj.__file__
    if PY2:
        # e.g.: foo.pyc -> foo.py
        filepath = os.path.splitext(filepath)[0] + ".py"
    filepath = os.path.abspath(filepath)
    return filepath


def abs_package_path(obj):
    """
    :return absolute directory path from __file__ attribute
    """
    return os.path.dirname(abs_py_path(obj))


def surround_code(code, info, indent=""):
    """
    Mark the beginning and end of the code.
    So, it's easier to find it in the generated bootstrap file ;)
    """
    comment_line = "#" * 79
    return "\n".join([
        "%s%s" % (indent, comment_line),
        "%s## %r START" % (indent, info),
        code.strip("\n"),
        "%s## %r END" % (indent, info),
        "%s%s" % (indent, comment_line),
        "", # add a new line at the end
    ])


def get_code(filename, cut_mark=None, indent=""):
    """
    Read a UTF-8 file and return the content after cut_mark, surrounded with comments.
    """
    if filename is None:
        return ""

    filename = os.path.abspath(os.path.normpath(filename))
    cutted_filename = cut_path(filename)

    print("Read code from: %r..." % cutted_filename)
    try:
        with codecs.open(filename, "r", encoding="UTF-8") as f:
            content = f.read()
    except UnicodeDecodeError as err:
        print("Error reading %r as UTF-8: %s" % (filename, err), file=sys.stderr)
        with codecs.open(filename, "r", encoding="UTF-8", errors="replace") as f:
            content = f.read()
    # content = content.decode("UTF-8")

    if cut_mark is not None:
        try:
            start_pos = content.index(cut_mark) + len(cut_mark)
        except ValueError as err:
            msg = (
                "Error: cut mark %r not found in %r: %s\n"
                " -------------- [begin file content] -------------- \n"
                "%s\n"
                " --------------- [end file content] --------------- \n"
            ) % (
                cut_mark, filename, err, content
            )
            raise ValueError(msg)

        content = content[start_pos:]

    return surround_code(content, cutted_filename, indent)