#!/usr/bin/env python
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :created: 2014 by JensDiemer.de
    :copyleft: 2014-2015 by the bootstrap_env team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function

from setuptools import setup, find_packages
import os
import sys

import bootstrap_env


if "publish" in sys.argv:
    try:
        # Test if wheel is installed, otherwise the user will only see:
        #   error: invalid command 'bdist_wheel'
        import wheel
    except ImportError as err:
        print("\nError: %s" % err)
        print("\nMaybe https://pypi.python.org/pypi/wheel is not installed or virtualenv not activated?!?")
        print("e.g.:")
        print("    ~/your/env/$ source bin/activate")
        print("    ~/your/env/$ pip install wheel")
        sys.exit(-1)

    import subprocess

    def call(*args):
        print("\nCall: %r\n" %  " ".join(args))
        try:
            return subprocess.check_output(args, universal_newlines=True)
        except subprocess.CalledProcessError as err:
            print("\n***ERROR:")
            print(err.output)
            raise

    # Check if we are on 'master' branch:
    output = call("git", "branch", "--no-color")
    if not "* master" in output:
        print("\nNOTE: It seems you are not on 'master':")
        print(output)
        if input("\nPublish anyhow? (Y/N)").lower() not in ("y", "j"):
            print("Bye.")
            sys.exit(-1)

    # publish only if git repro is clean:
    output = call("git", "status", "--porcelain")
    if output == "":
        print("OK")
    else:
        print("\n***ERROR: git repro not clean:")
        print(output)
        sys.exit(-1)

    # tag first (will raise a error of tag already exists)
    call("git", "tag", "v%s" % bootstrap_env.__version__)

    # build and upload to PyPi:
    call(sys.executable or "python", "setup.py", "sdist", "bdist_wheel", "upload")

    # push
    call("git", "push")
    call("git", "push", "--tags")

    sys.exit(0)


if "test" in sys.argv or "nosetests" in sys.argv:
    """
    nose is a optional dependency, so test import.
    Otherwise the user get only the error:
        error: invalid command 'nosetests'
    """
    try:
        import nose
    except ImportError as err:
        print("\nError: Can't import 'nose': %s" % err)
        print("\nMaybe 'nose' is not installed or virtualenv not activated?!?")
        print("e.g.:")
        print("    ~/your/env/$ source bin/activate")
        print("    ~/your/env/$ pip install nose")
        print("    ~/your/env/$ ./setup.py nosetests\n")
        sys.exit(-1)
    else:
        if "test" in sys.argv:
            print("\nPlease use 'nosetests' instead of 'test' to cover all tests!\n")
            print("e.g.:")
            print("     $ ./setup.py nosetests\n")
            sys.exit(-1)


PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


# convert creole to ReSt on-the-fly, see also:
# https://code.google.com/p/python-creole/wiki/UseInSetup
try:
    from creole.setup_utils import get_long_description
except ImportError as err:
    if "check" in sys.argv or "register" in sys.argv or "sdist" in sys.argv or "--long-description" in sys.argv:
        raise ImportError("%s - Please install python-creole >= v0.8 -  e.g.: pip install python-creole" % err)
    long_description = None
else:
    long_description = get_long_description(PACKAGE_ROOT)


setup(
    name="bootstrap_env",
    version=bootstrap_env.__version__,
    py_modules=["bootstrap_env"],
    provides=["bootstrap_env"],
    author="Jens Diemer",
    author_email="bootstrap_env@jensdiemer.de",
    description="Create a complete self contained virtualenv bootstrap file by enbed 'get-pip.py'",
    keywords="virtualenv pip",
    long_description=long_description,
    url="https://github.com/jedie/bootstrap_env",
    license="GPL v3+",
    install_requires=[
        "virtualenv",
    ],
    tests_require=[
        "nose", # https://pypi.python.org/pypi/nose
    ],
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Emulators",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    # TODO: test_suite="bootstrap_env.tests",
)
