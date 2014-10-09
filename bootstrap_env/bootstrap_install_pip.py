#!/usr/bin/env python
# coding: utf-8

"""
    used in 'create_bootstrap' to include it in the generated 'bootstrap.py' file

    http://virtualenv.readthedocs.org/en/latest/virtualenv.html#creating-your-own-bootstrap-scripts
"""

import os
import subprocess
import sys


# --- CUT here ---


def extend_parser(parser):
    sys.stdout.write("extend_parser called.\n")
    parser.add_option(
        '--install-pip',
        dest='install_pip',
        help="Only for internal usage!"
    )

def adjust_options(options, args):
    sys.stdout.write("adjust_options called.\n")

    # Importand, otherwise it failed with 'ImportError: No module named pip'
    # because the wheel files are not there
    options.no_setuptools=True

    sys.stdout.write("    options: %r\n" % options)
    sys.stdout.write("    args: %r\n" % args)

    if options.install_pip:
        print("install pip from self contained 'get_pip.py'")
        sys.argv = [sys.argv[0]]
        get_pip() # renamed main() from 'get_pip.py', it exists in the generated bootstrap file!
        print("pip is installed.")
        sys.exit(0)

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

def after_install(options, home_dir):
    install_pip(options, home_dir)
    sys.stdout.write("after_install from %r\n" % home_dir)