#!/usr/bin/env python
# coding: utf-8

"""
    used in 'create_bootstrap' to include it in the generated 'bootstrap.py' file.

    Important:
        There must be at least one other def function after extend_parser(), adjust_options() and after_install()
        Otherwise the last additional code will be not inserted!

    http://virtualenv.readthedocs.org/en/latest/virtualenv.html#creating-your-own-bootstrap-scripts

    :created: 2014 by JensDiemer.de
    :copyleft: 2014 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import subprocess
import sys


# --- CUT here ---

INSTALL_PIP_OPTION="--install-pip"


def extend_parser(parser):
    parser.add_option(
        INSTALL_PIP_OPTION,
        dest='install_pip',
        help="Only for internal usage!"
    )
    if INSTALL_PIP_OPTION in sys.argv:
        return # Skip the additional code, if pip should be installed


def adjust_options(options, args):
    # Importand, otherwise it failed with 'ImportError: No module named pip'
    # because the wheel files are not there
    options.no_setuptools=True

    if options.install_pip:
        print("install pip from self contained 'get_pip.py'")
        sys.argv = [sys.argv[0]]
        get_pip() # renamed main() from 'get_pip.py', it exists in the generated bootstrap file!
        print("pip is installed.")
        sys.exit(0)


def after_install(options, home_dir):
    install_pip(options, home_dir)


def install_pip(options, home_dir):
    abs_home_dir = os.path.abspath(home_dir)
    bin_dir = os.path.join(abs_home_dir, "bin")
    python_cmd = os.path.join(bin_dir, "python")

    bootstrap_file = os.path.abspath(sys.argv[0])
    assert os.path.isfile(bootstrap_file), "Path to self not found?!?! (%r not exists?!?!)" % bootstrap_file

    cmd=[python_cmd, bootstrap_file, "--install-pip"] + sys.argv[1:]
    print("call to install pip with: %r" % " ".join(cmd))
    subprocess.call(cmd,
        cwd=bin_dir,
        env={
            "VIRTUAL_ENV": home_dir,
            "PATH": bin_dir + ":" + os.environ["PATH"],
        }
    )