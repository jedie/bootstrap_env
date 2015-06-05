# coding: utf-8

"""
    :created: 2014 by JensDiemer.de
    :copyleft: 2014-2015 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

import os
import pprint
import sys

import pip
from pip.download import PipSession

def get_requirements(filepath, verbose=True):
    """
    returns pip requirements lines for installation.

    :param filepath: pip requirements file to read
    :param verbose: print informations?
    :return: list if requirements lines
    """
    requirements=pip.req.parse_requirements(filepath, session=PipSession())
    entries = []
    for req in requirements:
        if req.editable:
            # http://pip.readthedocs.org/en/latest/reference/pip_install.html#editable-installs

            # 7.0.1 … 6.1.0
            # https://github.com/pypa/pip/commit/e8e2566279879b7df04394edfcaa9c63c0ce9e67
            try:
                link = req.link # pip v7
            except AttributeError:
                link = req.url # pip v6

            entry = "--editable=%s" % link
        else:
            # install as normal PyPi package
            entry = req.name

        if verbose:
            print("\t* %r" % entry)

        if entry in entries:
            sys.stderr.write("\nWARNING: %r is duplicated defined in %r !\n" % (entry, filepath))
            continue
        entries.append(entry)

    if verbose:
        print()
    return entries


def requirements_definitions(base_path, filenames, verbose=True):
    """
    parse pip requirement files and create a string from them, for inserting into bootstrap file.
    The result is like:
        # requirements from normal_installation.txt
        NORMAL_INSTALLATION = ['virtualenv', 'bootstrap-env']

        # requirements from git_readonly_installation.txt
        GIT_READONLY_INSTALLATION = ['virtualenv', 'docutils',
         '--editable=git+https://github.com/jedie/bootstrap_env.git#egg=bootstrap_env']

        # requirements from developer_installation.txt
        DEVELOPER_INSTALLATION = ['virtualenv', 'docutils',
         '--editable=git+git@github.com:jedie/bootstrap_env.git#egg=bootstrap_env']

    :param base_path: directory of the given files
    :param filenames: list of requirement files
    :return: string of python code
    """
    content = []
    for filename in filenames:
        print("requirements from %r:" % filename)
        content.append("\n# requirements from %s" % filename)
        requirements_list = get_requirements(filepath=os.path.join(base_path, filename))
        req_type = os.path.splitext(filename)[0].upper()
        content.append(
            "%s = %s" % (req_type, pprint.pformat(requirements_list))
        )

    return "\n".join(content)