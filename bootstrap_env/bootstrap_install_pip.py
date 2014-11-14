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

# imports not really needed and just for the editor warning ;)
import os
import subprocess
import sys

from bootstrap_env.create_bootstrap import get_pip

# --- CUT here ---


INSTALL_PIP_OPTION="--install-pip"


class EnvSubprocess(object):
    """
    Use to install pip and useful also to install other packages in after_install.
    """
    def __init__(self, home_dir):
        self.abs_home_dir = os.path.abspath(home_dir)

        if sys.platform in ['win32','cygwin','win64']:
            self.bin_dir = os.path.join(self.abs_home_dir, "Scripts")
        else:
            self.bin_dir = os.path.join(self.abs_home_dir, "bin")

        self.python_cmd = os.path.join(self.bin_dir, "python")
        self.pip_cmd = os.path.join(self.bin_dir, "pip")

        self.subprocess_defaults = {
            "cwd": self.bin_dir,
            "env": {
                "VIRTUAL_ENV": self.abs_home_dir,
                "PATH": self.bin_dir + os.pathsep + os.environ["PATH"],
            }
        }
        try:
            # Work-a-round for http://bugs.python.org/issue20614 :
            #       Python3 will crash under windows without SYSTEMROOT
            self.subprocess_defaults["env"]["SYSTEMROOT"] = os.environ['SYSTEMROOT']
        except KeyError:
            pass

    def _subprocess(self, cmd):
        print("call %r" % " ".join(cmd))
        subprocess.call(cmd, **self.subprocess_defaults)

    def call_env_python(self, cmd):
        self._subprocess([self.python_cmd] + cmd)

    def call_env_pip(self, cmd):
        self._subprocess([self.pip_cmd] + cmd)


def _install_pip(options, home_dir):
    print("Install pip...")
    bootstrap_file = os.path.abspath(sys.argv[0])
    assert os.path.isfile(bootstrap_file), "Path to self not found?!?! (%r not exists?!?!)" % bootstrap_file

    env_subprocess = EnvSubprocess(home_dir)
    env_subprocess.call_env_python([bootstrap_file, "--install-pip", env_subprocess.abs_home_dir])


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
    _install_pip(options, home_dir)
