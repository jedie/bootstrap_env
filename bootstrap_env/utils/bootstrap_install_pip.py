#!/usr/bin/env python
# coding: utf-8

"""
    used in 'create_bootstrap' to include it in the generated 'bootstrap.py' file.

    Important:
        There must be at least one other def function after extend_parser(), adjust_options() and after_install()
        Otherwise the last additional code will be not inserted!

    http://virtualenv.readthedocs.org/en/latest/virtualenv.html#creating-your-own-bootstrap-scripts

    :created: 2014 by JensDiemer.de
    :copyleft: 2014-2015 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

# imports not really needed and just for the editor warning ;)
import os
import subprocess
import sys

from bootstrap_env.utils.get_pip import get_pip

# --- CUT here ---

INSTALL_PIP_OPTION="--install-pip"


class EnvSubprocess(object):
    """
    Use to install pip and useful also to install other packages in after_install.
    """
    def __init__(self, home_dir):
        self.abs_home_dir = os.path.abspath(home_dir)

        self.bin_dir = self._get_bin_dir()
        self.python_cmd = self._get_python_cmd()
        self.pip_cmd = None # Will be set on first call

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

    def _get_bin_dir(self):
        """
        Normaly we have a ...env/bin/ dir.
        But under Windows we have ...env/Scripts/
        But not PyPy2 under Windows, see:
        https://bitbucket.org/pypy/pypy/issues/2125/tcl-doesnt-work-inside-a-virtualenv-on#comment-21247266

        So just try to test via os.path.isdir()
        """
        for subdir in ("bin", "Scripts"):
            bin_dir = os.path.join(self.abs_home_dir, subdir)
            if os.path.isdir(bin_dir):
                print("bin dir: %r" % bin_dir)
                return bin_dir
        raise RuntimeError("Can't find 'bin/Scripts' dir in: %r" % self.abs_home_dir)

    def _get_python_cmd(self):
        """
        return the python executable in the virtualenv.
        Try first sys.executable but use fallbacks.
        """
        file_names = ["pypy.exe", "python.exe", "python"]
        executable = sys.executable
        if executable is not None:
            executable = os.path.split(executable)[1]
            file_names.insert(0, executable)

        return self._get_bin_file(*file_names)

    def _get_bin_file(self, *file_names):
        for file_name in file_names:
            file_path = os.path.join(self.bin_dir, file_name)
            if os.path.isfile(file_path):
                print("Use: %r" % file_path)
                return file_path
        raise RuntimeError(
            "Can't find file in %r. Tested file names are: %r" % (self.bin_dir, file_names)
        )

    def _subprocess(self, cmd):
        print("\ncall %r" % " ".join(cmd))
        subprocess.call(cmd, **self.subprocess_defaults)

    def call_env_python(self, cmd):
        self._subprocess([self.python_cmd] + cmd)

    def call_env_pip(self, cmd):
        if self.pip_cmd is None:
            self.pip_cmd = self._get_bin_file("pip.exe", "pip")
        self._subprocess([self.pip_cmd] + cmd)


def _install_pip(options, home_dir):
    print("\nInstall pip...")
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
    options.no_pip=True
    options.no_wheel=True

    if options.install_pip:
        print("\ninstall pip from self contained 'get_pip.py'")
        sys.argv = [sys.argv[0]]
        get_pip() # renamed main() from 'get_pip.py', it exists in the generated bootstrap file!
        print("\npip is installed.\n")
        sys.exit(0)


def after_install(options, home_dir):
    _install_pip(options, home_dir)
